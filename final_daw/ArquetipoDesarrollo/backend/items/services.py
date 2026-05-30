import io
import logging
import os
import zipfile

import boto3
from botocore.client import Config
from django.utils import timezone

from django.core.exceptions import ValidationError
from .models import Item
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db.models import Exists, OuterRef

logger = logging.getLogger(__name__)


class ItemService:
    # =========================================================
    # SECCIÓN 1: Validaciones y auxiliares
    # =========================================================

    # Validamos que no se den bucles en el arbol (Por ejemplo mover una carpeta dentro de si misma)
    @staticmethod
    def check_cycle(item, nueva_carpeta_padre):
        actual = nueva_carpeta_padre

        while actual:
            if actual.id == item.id:
                return True
            actual = actual.padre

        return False
    
    @staticmethod
    def recolectar_descendientes_id(root_ids, usuario):
        """
        Devuelve todos los ids raíz + descendientes del usuario
        sin hacer N+1.
        """
        all_ids = set(int(i) for i in root_ids)
        frontier = set(all_ids)

        while frontier:
            children = set(
                Item.objects.filter(
                    usuario=usuario,
                    padre_id__in=frontier,
                ).values_list("id", flat=True)
            )
            children -= all_ids
            if not children:
                break

            all_ids |= children
            frontier = children

        return all_ids

    @staticmethod
    def get_s3_client():
        return boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            #Añado esto porque me estaba dando problema para descargar
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    @staticmethod
    def get_s3_keys_for_items(items_qs):
        """
        Extrae las keys de S3 de los items tipo archivo.
        """
        return list(
            items_qs.exclude(file="").exclude(file__isnull=True).values_list("file", flat=True)
        )
    
    @staticmethod
    def delete_s3_keys(keys, bucket_name):
        if not keys:
            return

        s3 = ItemService.get_s3_client()

        for i in range(0, len(keys), 1000):
            batch = keys[i:i + 1000]
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    "Objects": [{"Key": key} for key in batch],
                    "Quiet": True,
                }
            )

    @staticmethod
    def eliminar_items_fisicos(ids, usuario, bucket_name):
        """
        Borra físicamente items (solo los que están en papelera) y sus descendientes.
        """
        # Filtramos solo items marcados como eliminados para mayor seguridad
        ids_validados = list(
            Item.objects.filter(
                id__in=ids,
                usuario=usuario,
                eliminado=True,
            ).values_list('id', flat=True)
        )

        if not ids_validados:
            return {'deleted_count': 0, 's3_keys_deleted': 0}

        all_ids = ItemService.recolectar_descendientes_id(ids_validados, usuario)
        items_qs = Item.objects.filter(usuario=usuario, id__in=all_ids)
        s3_keys = ItemService.get_s3_keys_for_items(items_qs)

        with transaction.atomic():
            ItemService.delete_s3_keys(s3_keys, bucket_name)
            deleted_count, _ = items_qs.delete()

        return {
            'deleted_count': deleted_count,
            's3_keys_deleted': len(s3_keys),
        }

    
    @staticmethod
    def vaciar_papelera(usuario, bucket_name):
        trash_ids = list(
            Item.objects.filter(usuario=usuario, eliminado=True).values_list("id", flat=True)
        )

        if not trash_ids:
            return {
                "deleted_count": 0,
                "s3_keys_deleted": 0,
            }

        return ItemService.eliminar_items_fisicos(trash_ids, usuario, bucket_name)

    @staticmethod
    def restaurar_items(ids, usuario):
        all_ids = ItemService.recolectar_descendientes_id(ids, usuario)

        return Item.objects.filter(
            usuario=usuario,
            id__in=all_ids
        ).update(
            eliminado=False,
            fecha_eliminado=None
        )

    @staticmethod
    def eliminar_del_indice(item_id):
        """Elimina el documento de Elasticsearch. Si no existe, no hace nada."""
        try:
            from .documents import ItemDocument
            from elasticsearch.exceptions import NotFoundError
            ItemDocument.get(id=item_id).delete()
        except Exception as e:
            logger.warning("No se pudo eliminar del índice item %s: %s", item_id, e)

    # =========================================================
    # SECCIÓN 2: Consultas y navegacion
    # =========================================================

    # Prefijos soportados campo:valor
    _PREFIJOS_CAMPO = {
        'artista': ('match', 'meta_artista'),
        'artist':  ('match', 'meta_artista'),
        'album':   ('match', 'meta_album'),
        'titulo':  ('match', 'meta_titulo'),
        'title':   ('match', 'meta_titulo'),
        'genero':  ('match', 'meta_genero'),
        'genre':   ('match', 'meta_genero'),
        'camara':  ('match', 'meta_camara_modelo'),
        'nombre':  ('match', 'nombre'),
        'año':     ('year',  None),
        'year':    ('year',  None),
        'tipo':    ('tipo',  None),
    }

    _TIPOS_MIME = {
        'audio':  'audio/',
        'imagen': 'image/',
        'image':  'image/',
        'texto':  'text/',
        'text':   'text/',
    }

    @staticmethod
    def _parsear_query(q):
        must_extra = []
        filter_extra = []
        texto_libre = []

        for token in q.split():
            if ':' not in token:
                texto_libre.append(token)
                continue

            prefijo, _, valor = token.partition(':')
            mapping = ItemService._PREFIJOS_CAMPO.get(prefijo.lower())

            if not mapping or not valor:
                texto_libre.append(token)
                continue

            kind, campo = mapping

            if kind == 'match':
                must_extra.append(
                    {'match': {campo: {'query': valor, 'fuzziness': 'AUTO'}}}
                )
            elif kind == 'year':
                try:
                    filter_extra.append({'term': {'meta_anno': int(valor)}})
                except ValueError:
                    texto_libre.append(token)
            elif kind == 'tipo':
                valor_lower = valor.lower()
                if valor_lower == 'carpeta':
                    filter_extra.append({'term': {'tipo': 'carpeta'}})
                else:
                    mime_prefix = ItemService._TIPOS_MIME.get(valor_lower)
                    if mime_prefix:
                        filter_extra.append({'prefix': {'mime_type': mime_prefix}})
                    else:
                        texto_libre.append(token)

        return must_extra, filter_extra, ' '.join(texto_libre)

    @staticmethod
    def buscar_items(usuario, q):
        from elasticsearch import Elasticsearch

        es = Elasticsearch(**settings.ELASTICSEARCH_DSL['default'])

        must_extra, filter_extra, texto_libre = ItemService._parsear_query(q)

        must = []
        if texto_libre:
            must.append({
                'multi_match': {
                    'query': texto_libre,
                    'fields': [
                        'nombre^3', 'contenido^0.5', 'meta_titulo^2',
                        'meta_artista', 'meta_album', 'meta_genero',
                        'meta_camara_marca', 'meta_camara_modelo',
                    ],
                    'fuzziness': 'AUTO',
                }
            })
        must.extend(must_extra)

        bool_query = {
            'filter': [
                {'term': {'usuario_id': usuario.id}},
                {'term': {'eliminado': False}},
                *filter_extra,
            ],
        }
        if must:
            bool_query['must'] = must

        respuesta = es.search(index='items', size=50, min_score=1.0, query={'bool': bool_query})
        ids = [int(hit['_id']) for hit in respuesta['hits']['hits']]

        if not ids:
            return []

        hijos = Item.objects.filter(padre=OuterRef('pk'), eliminado=False)
        items_map = {
            item.id: item
            for item in Item.objects.filter(
                id__in=ids, usuario=usuario, eliminado=False
            ).annotate(tiene_hijos=Exists(hijos))
        }
        return [items_map[id_] for id_ in ids if id_ in items_map]

    @staticmethod
    def obtener_breadcrumb(usuario, carpeta_id):
        ruta_base = [{"id": None, "label": "Inicio"}]
        
        # Si no hay ID o es la raíz, devolvemos solo inicio
        if not carpeta_id:
            return ruta_base

        try:
            # Aseguro que id sea un entero para no tener problema
            id_actual = int(carpeta_id)
        except (ValueError, TypeError):
            return ruta_base

        # 1. Traemos TODAS las carpetas (incluidas las eliminadas)
        carpetas = Item.objects.filter(
            usuario=usuario, 
            tipo='carpeta'
        ).values('id', 'nombre', 'padre_id')

        # 2. Mapa en memoria
        mapa_carpetas = {c['id']: c for c in carpetas}

        # 3. Construcción del camino
        nodos_padre = []

        while id_actual is not None:
            carpeta = mapa_carpetas.get(id_actual)
            
            if not carpeta:
                # Si no encontramos la carpeta en el mapa puede ser que el ID no exista o no sea del usuario
                break
            
            nodos_padre.append({
                "id": carpeta['id'],
                "label": carpeta['nombre']
            })
            
            # Saltamos al padre
            id_actual = carpeta['padre_id']

        # 4. Invertimos para ir de Raíz -> Hijo
        ruta_base.extend(reversed(nodos_padre))
        return ruta_base

    # =========================================================
    # SECCIÓN 3: Operaciones de escritura (CRUD)
    # =========================================================

    @staticmethod
    def crear_item(usuario, datos, fichero=None): 
        # Creo el item base
        item = Item(usuario=usuario, **datos)

        print(datos)
        # Si es Carpeta
        if item.tipo == Item.Tipo.CARPETA:
            return ItemService.guardar_item(item)
        
        # Si es Archivo
        if not fichero:
            raise ValidationError("Archivo requerido")
        
        # Guardo el fichero real en Garage a través de Django
        item.file = fichero

        item.tamano_bytes = fichero.size
        item.mime_type = fichero.content_type

        return ItemService.guardar_item(item)        


    @staticmethod
    def mover_item(item, nueva_carpeta_padre):
        if ItemService.check_cycle(item, nueva_carpeta_padre):
            raise ValidationError("No puedes crear ciclos")

        item.padre = nueva_carpeta_padre

        return ItemService.guardar_item(item)
    
    @staticmethod
    def _nombre_disponible(usuario, nombre, padre):
        existe = Item.objects.filter(
            usuario=usuario, padre=padre, nombre=nombre, eliminado=False
        ).exists()
        if not existe:
            return nombre

        base, ext = os.path.splitext(nombre)
        contador = 1
        while True:
            candidato = f"{base} ({contador}){ext}"
            if not Item.objects.filter(
                usuario=usuario, padre=padre, nombre=candidato, eliminado=False
            ).exists():
                return candidato
            contador += 1

    @staticmethod
    def guardar_item(item):
        try:
            item.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        item.save()
        return item

    # =========================================================
    # SECCIÓN 4: Gestión de estados (Papelera, Favoritos etc.)
    # =========================================================

    # Método Soft Delete - Mandar a la papelera
    @staticmethod
    def mover_a_papelera(ids, usuario):
        all_ids = ItemService.recolectar_descendientes_id(ids, usuario)

        return Item.objects.filter(
            usuario=usuario,
            id__in=all_ids
        ).update(
            eliminado=True,
            fecha_eliminado=timezone.now()
        )
    
    @staticmethod
    def marcar_favorito(ids, usuario):
        items = Item.objects.filter(id__in=ids, usuario=usuario)

        # Revisar esto!!! POrque si alguna esta y otro no, no tiene sentid oque ahora sean todos favoritos!!!!!!!!!!!!!!!
        todos_favoritos = all(item.favorito for item in items)
        nuevo_valor = not todos_favoritos

        items.update(favorito=nuevo_valor)
        return nuevo_valor

    # =========================================================
    # SECCIÓN 5: Descarga de archivos
    # =========================================================

    @staticmethod
    def generar_url_descarga(item):
        """
        Genera una presigned URL para descarga directa de un único archivo.
        """
        public_endpoint = getattr(settings, "GARAGE_PUBLIC_URL", settings.AWS_S3_ENDPOINT_URL)

        client = boto3.client(
            "s3",
            endpoint_url=public_endpoint,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

        return client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": str(item.file),
                "ResponseContentDisposition": f'attachment; filename="{item.nombre}"',
            },
            ExpiresIn=300,
        )

    @staticmethod
    def generar_url_preview(item):
        """Genera una presigned URL para previsualización (image, audio, PDF)."""
        public_endpoint = getattr(settings, "GARAGE_PUBLIC_URL", settings.AWS_S3_ENDPOINT_URL)

        client = boto3.client(
            "s3",
            endpoint_url=public_endpoint,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

        params = {
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": str(item.file),
            "ResponseContentDisposition": f'inline; filename="{item.nombre}"',
        }
        if item.mime_type:
            params["ResponseContentType"] = item.mime_type

        return client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=300,
        )

    @staticmethod
    def recolectar_archivos_para_zip(root_ids, usuario):
        """
        Recorre el árbol de ítemsy devuelve una lista de manteniendo la estructura de carpetas.
        """
        resultado = []
        # Mapa id
        pendientes = {int(i): "" for i in root_ids}

        while pendientes:
            items = Item.objects.filter(
                id__in=list(pendientes.keys()),
                usuario=usuario,
                eliminado=False,
            )
            carpetas_con_prefijo = {}

            for item in items:
                prefijo = pendientes[item.id]
                if item.tipo == Item.Tipo.ARCHIVO:
                    resultado.append((item, prefijo + item.nombre))
                elif item.tipo == Item.Tipo.CARPETA:
                    carpetas_con_prefijo[item.id] = prefijo + item.nombre + "/"

            if not carpetas_con_prefijo:
                break

            hijos = Item.objects.filter(
                padre_id__in=carpetas_con_prefijo.keys(),
                usuario=usuario,
                eliminado=False,
            ).values("id", "padre_id")

            pendientes = {
                hijo["id"]: carpetas_con_prefijo[hijo["padre_id"]]
                for hijo in hijos
            }

        return resultado

    @staticmethod
    def generar_url_presignada_subida(key):
        """
        Genera una presigned URL para que el navegador haga PUT directamente a Garage.
        Usa el endpoint PÚBLICO para que la firma SigV4 coincida con el host
        que verá el navegador.
        """
        public_endpoint = getattr(settings, 'GARAGE_PUBLIC_URL', settings.AWS_S3_ENDPOINT_URL)

        client = boto3.client(
            's3',
            endpoint_url=public_endpoint,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'},
            ),
        )

        return client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
            },
            ExpiresIn=3600,
            HttpMethod='PUT',
        )

    @staticmethod
    def registrar_item_subido(usuario, nombre, padre, key, tamano_bytes, mime_type):
        nombre = ItemService._nombre_disponible(usuario, nombre, padre)
        item = Item(
            usuario=usuario,
            nombre=nombre,
            tipo=Item.Tipo.ARCHIVO,
            padre=padre,
            tamano_bytes=tamano_bytes or 0,
            mime_type=mime_type or 'application/octet-stream',
        )
        item.file = key
        return ItemService.guardar_item(item)

    # Límite de descarga por tipo MIME antes de intentar extraer metadatos
    _LIMITE_DESCARGA_BYTES = {
        'audio': 50  * 1024 * 1024,  # 50 MB — cubre MP3/FLAC; WAV sin tags no aporta nada
        'image': 40  * 1024 * 1024,  # 40 MB — cubre JPEG/PNG/WebP 
        'text':   5  * 1024 * 1024,  # 5 MB  — coherente con LIMITE_CONTENIDO_BYTES del extractor
    }

    @staticmethod
    def indexar_item(item):
        """
        Extrae metadatos del archivo y actualiza el índice de Elasticsearch.
        Si el archivo supera el límite para su tipo, se indexa solo con los
        metadatos básicos (nombre, tamaño…) sin descargar el contenido.
        """
        if item.tipo != Item.Tipo.ARCHIVO or not item.file:
            return
        try:
            from .extractors import extraer
            from .documents import ItemDocument

            mime_prefix = (item.mime_type or '').split('/')[0].lower()
            limite = ItemService._LIMITE_DESCARGA_BYTES.get(mime_prefix)
            tamano = item.tamano_bytes or 0

            if limite is not None and tamano <= limite:
                s3 = ItemService.get_s3_client()
                obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(item.file))
                datos = obj['Body'].read()

                resultado = extraer(datos, item.mime_type or '', tamano)
                metadatos = resultado['metadatos']
                if resultado['contenido']:
                    metadatos['contenido'] = resultado['contenido']

                item.metadatos = metadatos
                Item.objects.filter(pk=item.pk).update(metadatos=metadatos)

            ItemDocument().update(item)
        except Exception as e:
            logger.warning("No se pudo indexar item %s: %s", item.id, e)

    @staticmethod
    def construir_zip(archivos_con_ruta, bucket_name):
        """
        Descarga cada archivo desde Garage S3 y lo empaqueta en un ZIP
        en memoria (io.BytesIO). Devuelve el buffer listo para enviar.
        """
        s3 = ItemService.get_s3_client()
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for item, zip_path in archivos_con_ruta:
                obj = s3.get_object(Bucket=bucket_name, Key=str(item.file))
                zf.writestr(zip_path, obj["Body"].read())

        buffer.seek(0)
        return buffer