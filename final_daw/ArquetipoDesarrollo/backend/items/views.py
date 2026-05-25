import os
import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.db import transaction

from core.settings import development
from .models import Item
from .serializers import ItemSerializer
from .services import ItemService


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    # FILTRADO BASE
    def get_queryset(self):
        user = self.request.user
        qs = Item.objects.filter(usuario=user)

        # 1. Parámetros
        carpeta_id = self.request.query_params.get("carpeta")
        es_papelera = self.request.query_params.get("papelera") == "true"
        es_favorito = self.request.query_params.get("favorito") == "true"
        
        # 2. Estado de eliminación (Papelera vs Normal)
        if es_papelera:
            qs = qs.filter(eliminado=True)
        else:
            qs = qs.filter(eliminado=False)
        
        # 3. Lógica de Navegación vs Filtrado
        if carpeta_id:
            qs = qs.filter(padre_id=carpeta_id)
        else:
            if es_favorito:
                qs = qs.filter(favorito=True)
            elif not es_papelera:
                qs = qs.filter(padre__isnull=True)

        # 4. Optimización y orden
        hijos = Item.objects.filter(padre=OuterRef("pk"), eliminado=False)
        return qs.annotate(tiene_hijos=Exists(hijos)).order_by("-tipo", "nombre")
    
    # MÉTODOS ESTÁNDAR
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        carpeta_id = request.query_params.get('carpeta')
        breadcrumb = ItemService.obtener_breadcrumb(request.user, carpeta_id)
        return Response({'items': serializer.data, 'breadcrumb': breadcrumb})


    def perform_create(self, serializer):
        blob = self.request.FILES.get('file')
        item = ItemService.crear_item(
            usuario=self.request.user,
            datos=serializer.validated_data,
            fichero=blob,
        )
        serializer.instance = item

    # =========================================================
    # ACCIONES SOBRE ITEMS
    # =========================================================

    @action(detail=True, methods=['post'])
    def renombrar(self, request, pk=None):
        item = self.get_object()
        nuevo_nombre = request.data.get('nombre')
        if not nuevo_nombre:
            return Response(
                {'detail': 'El nombre es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.nombre = nuevo_nombre
        item.save()

        if item.tipo == Item.Tipo.ARCHIVO:
            try:
                from .documents import ItemDocument
                doc = ItemDocument.get(id=item.pk)
                doc.update(nombre=nuevo_nombre, nombre_raw=nuevo_nombre)
            except Exception:
                pass

        return Response({'mensaje': 'Renombrado correctamente', 'nombre': item.nombre})

    @action(detail=False, methods=['post'])
    def favorito(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'detail': 'No se han enviado elementos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            nuevo_valor = ItemService.marcar_favorito(ids=ids, usuario=request.user)
            return Response({
                'detail': 'Favorito actualizado correctamente.',
                'favorito': nuevo_valor,
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def trash(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'detail': 'No se han enviado elementos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            cantidad = ItemService.mover_a_papelera(ids=ids, usuario=request.user)
            return Response({'detail': f'Se han movido {cantidad} elementos a la papelera.'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def eliminar_definitivo(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'detail': 'No se han enviado elementos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_ids = ItemService.recolectar_descendientes_id(ids, request.user)
        ids_archivos = list(
            Item.objects.filter(
                id__in=all_ids,
                usuario=request.user,
                tipo=Item.Tipo.ARCHIVO,
                eliminado=True,
            ).values_list('id', flat=True)
        )

        try:
            result = ItemService.eliminar_items_fisicos(
                ids=ids,
                usuario=request.user,
                bucket_name=development.AWS_STORAGE_BUCKET_NAME,
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for item_id in ids_archivos:
            ItemService.eliminar_del_indice(item_id)

        return Response({
            'detail': f"Se han eliminado {result['deleted_count']} elementos permanentemente.",
            'deleted_count': result['deleted_count'],
            's3_keys_deleted': result['s3_keys_deleted'],
        })

    @action(detail=False, methods=['post'])
    def restaurar(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'detail': 'No se han enviado elementos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            restaurados = ItemService.restaurar_items(ids=ids, usuario=request.user)
            return Response({'detail': f'Se han restaurado {restaurados} elementos.'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def restaurar_papelera(self, request):
        ids = list(
            Item.objects.filter(
                usuario=request.user,
                eliminado=True,
            ).values_list('id', flat=True)
        )
        try:
            restaurados = ItemService.restaurar_items(ids=ids, usuario=request.user)
            return Response({'detail': f'Se han restaurado {restaurados} elementos.'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def vaciar_papelera(self, request):
        ids_archivos = list(
            Item.objects.filter(
                usuario=request.user,
                eliminado=True,
                tipo=Item.Tipo.ARCHIVO,
            ).values_list('id', flat=True)
        )

        try:
            result = ItemService.vaciar_papelera(
                usuario=request.user,
                bucket_name=development.AWS_STORAGE_BUCKET_NAME,
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for item_id in ids_archivos:
            ItemService.eliminar_del_indice(item_id)

        return Response({
            'detail': 'Papelera vaciada correctamente.',
            'deleted_count': result['deleted_count'],
            's3_keys_deleted': result['s3_keys_deleted'],
        })

    # =========================================================
    # DESCARGA
    # =========================================================

    @action(detail=True, methods=['get'])
    def descargar_archivo(self, request, pk=None):
        """Devuelve una presigned URL de descarga directa para un archivo."""
        item = self.get_object()
        if item.tipo != 'archivo' or not item.file:
            return Response(
                {'detail': 'El elemento no es un archivo descargable.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'url': ItemService.generar_url_descarga(item)})

    @action(detail=False, methods=['post'])
    def descargar(self, request):
        """
        Construye un ZIP en memoria con todos los ítems seleccionados
        (resuelve carpetas recursivamente) y lo retorna como stream.

        REVISAR ESTO PORQUE IGUAL SI TIENE QUE DEVOLVER UN ARCHIVO MUY GRANDE LA LIOOO, AHORA CARGA TDO EL OBJETO EN MEMORIA
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'detail': 'No se han enviado elementos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        archivos_con_ruta = ItemService.recolectar_archivos_para_zip(
            root_ids=ids,
            usuario=request.user,
        )

        if not archivos_con_ruta:
            return Response(
                {'detail': 'No se encontraron archivos para descargar.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        zip_buffer = ItemService.construir_zip(
            archivos_con_ruta=archivos_con_ruta,
            bucket_name=development.AWS_STORAGE_BUCKET_NAME,
        )

        response = FileResponse(
            zip_buffer,
            as_attachment=True,
            filename='descarga.zip',
        )
        response['Content-Type'] = 'application/zip'
        return response


    # =========================================================
    # BÚSQUEDA
    # =========================================================

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        GET /api/items/buscar/?q=<texto>
        Devuelve items ordenados por relevancia de Elasticsearch.
        """
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response(
                {'detail': 'El parámetro q es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            resultados = ItemService.buscar_items(usuario=request.user, q=q)
        except Exception as e:
            return Response(
                {'detail': 'Error al conectar con el motor de búsqueda.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = self.get_serializer(resultados, many=True)
        return Response({'items': serializer.data, 'query': q})

    # =========================================================
    # SUBIDA PRESIGNADA (De Vue a Garage directo)
    # =========================================================

    @action(detail=False, methods=['post'])
    def solicitar_subida(self, request):
        """
        Paso 1: devuelve una presigned PUT URL para que Vue suba el fichero directamente a Garage sin pasar por Django.
        Body: { nombre, mime_type? }
        Response: { url_subida, key }
        """
        nombre = request.data.get('nombre', '').strip()
        mime_type = request.data.get('mime_type', 'application/octet-stream')

        if not nombre:
            return Response({'detail': 'El nombre es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        _, extension = os.path.splitext(nombre)
        key = f"users/{request.user.id}/{uuid.uuid4().hex}{extension}"

        url_subida = ItemService.generar_url_presignada_subida(key)
        return Response({'url_subida': url_subida, 'key': key})

    @action(detail=False, methods=['post'])
    def confirmar_subida(self, request):
        """
        Paso 2: registra el Item en la BD tras la subida directa a Garage.
        Body: { nombre, key, padre?, tamano_bytes, mime_type }
        """
        nombre = request.data.get('nombre', '').strip()
        key = request.data.get('key', '').strip()
        padre_id = request.data.get('padre', None)
        tamano_bytes = request.data.get('tamano_bytes', 0)
        mime_type = request.data.get('mime_type', 'application/octet-stream')

        if not nombre or not key:
            return Response({'detail': 'nombre y key son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

        padre = None
        if padre_id:
            try:
                padre = Item.objects.get(id=padre_id, usuario=request.user, tipo='carpeta', eliminado=False)
            except Item.DoesNotExist:
                return Response({'detail': 'Carpeta padre no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = ItemService.registrar_item_subido(
                usuario=request.user,
                nombre=nombre,
                padre=padre,
                key=key,
                tamano_bytes=tamano_bytes,
                mime_type=mime_type,
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        ItemService.indexar_item(item)

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def crear_arbol_carpetas(self, request):
        """
        Recibe una lista de rutas relativas de carpetas (ordenadas de raíz a hoja) y las crea devolviendo el mapa { ruta: id }.
        Body: { rutas: ["carpeta", "carpeta/sub", ...], padre: null | id }
        """
        rutas = request.data.get('rutas', [])
        padre_id = request.data.get('padre', None)
        
        if not rutas:
            return Response({'mapa': {}})
        
        mapa = {}
        
        padre_raiz = None
        if padre_id:
            try:
                padre_raiz = Item.objects.get(id=padre_id, usuario=request.user, tipo='carpeta')
            except Item.DoesNotExist:
                return Response({'detail': 'Carpeta padre no encontrada.'}, status=404)
        
        try:
            with transaction.atomic():
                for ruta in rutas:
                    partes = ruta.split('/')
                    nombre = partes[-1]
                    
                    # El padre de esta carpeta es la ruta padre dentro del mapa
                    if len(partes) == 1:
                        padre = padre_raiz
                    else:
                        ruta_padre = '/'.join(partes[:-1])
                        padre_id_local = mapa.get(ruta_padre)
                        if padre_id_local is None:
                            return Response(
                                {'detail': f'Ruta padre no encontrada: {ruta_padre}'},
                                status=400
                            )
                        padre = Item.objects.get(id=padre_id_local)
                    
                    item = Item(
                        usuario=request.user,
                        nombre=nombre,
                        tipo=Item.Tipo.CARPETA,
                        padre=padre,
                    )
                    ItemService.guardar_item(item)
                    mapa[ruta] = item.id
                    
        except Exception as e:
            return Response({'detail': str(e)}, status=400)
        
        return Response({'mapa': mapa})
