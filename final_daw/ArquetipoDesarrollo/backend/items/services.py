from django.core.exceptions import ValidationError
from .models import Item


class ItemService:

    # Validamos que no se den bucles en el arbol (Por ejemplo mover una carpeta dentro de si misma)
    @staticmethod
    def check_cycle(item, nueva_carpeta_padre):
        actual = nueva_carpeta_padre

        while actual:
            if actual.id == item.id:
                return True
            actual = actual.padre

        return False

    # Aplicamos reglas de almacenamietno
    @staticmethod
    def aplicar_reglas_almacenamiento(item, usuario=None, fichero=None):

        # Si es carpeta, no tiene datos de archivo
        if item.tipo == Item.Tipo.CARPETA:
            item.ruta = None
            item.tamano_bytes = None
            item.mime_type = None
            return item

        # Si es archivo, debe existir archivo
        if not fichero:
            raise ValidationError("Archivo requerido")

        item.ruta = f"uploads/{usuario.id}/{fichero.name}"
        item.tamano_bytes = fichero.size
        item.mime_type = fichero.content_type

        return item

    # GUARDADO CENTRALIZADO

    @staticmethod
    def guardar_item(item):
        item.full_clean()
        item.save()
        return item

    # CREAR ITEM

    @staticmethod
    def crear_item(usuario, datos, fichero=None): 
        
        # Creamos la instancia del modelo con los datos del formulario
        nuevo_item = Item(usuario=usuario, **datos)

        # Pasamos el archivo  a las reglas de almacenamiento
        nuevo_item = ItemService.aplicar_reglas_almacenamiento(
            item=nuevo_item,
            usuario=usuario,
            fichero=fichero # Aquí le pasas el objeto que recibiste arriba
        )
        
        return ItemService.guardar_item(nuevo_item)

    # MOVER ITEM
    @staticmethod
    def mover_item(item, nueva_carpeta_padre):

        if ItemService.check_cycle(item, nueva_carpeta_padre):
            raise ValidationError("No puedes crear ciclos")

        item.padre = nueva_carpeta_padre

        return ItemService.guardar_item(item)