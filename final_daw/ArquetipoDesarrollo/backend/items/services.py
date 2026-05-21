import boto3
from django.utils import timezone

from django.core.exceptions import ValidationError
from .models import Item
from django.db import transaction
from django.conf import settings



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
        Borra físicamente items y sus descendientes.
        """
        all_ids = ItemService.recolectar_descendientes_id(ids, usuario)

        items_qs = Item.objects.filter(usuario=usuario, id__in=all_ids)

        s3_keys = ItemService.get_s3_keys_for_items(items_qs)

        with transaction.atomic():
            ItemService.delete_s3_keys(s3_keys, bucket_name)
            deleted_count, _ = items_qs.delete()

        return {
            "deleted_count": deleted_count,
            "s3_keys_deleted": len(s3_keys),
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
    # =========================================================
    # SECCIÓN 2: Consultas y navegacion
    # =========================================================

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
                # Si no encontramos la carpeta en el mapa, 
                # puede ser que el ID no exista o no sea del usuario
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
    def guardar_item(item):
        item.full_clean()
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
        return Item.objects.filter(id__in=ids, usuario=usuario).update(
            favorito=True
        )