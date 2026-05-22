from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from django.db.models import Exists, OuterRef

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
        try:
            result = ItemService.eliminar_items_fisicos(
                ids=ids,
                usuario=request.user,
                bucket_name=development.AWS_STORAGE_BUCKET_NAME,
            )
            return Response({
                'detail': f"Se han eliminado {result['deleted_count']} elementos permanentemente.",
                'deleted_count': result['deleted_count'],
                's3_keys_deleted': result['s3_keys_deleted'],
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            result = ItemService.vaciar_papelera(
                usuario=request.user,
                bucket_name=development.AWS_STORAGE_BUCKET_NAME,
            )
            return Response({
                'detail': 'Papelera vaciada correctamente.',
                'deleted_count': result['deleted_count'],
                's3_keys_deleted': result['s3_keys_deleted'],
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)