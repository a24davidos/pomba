# services.py
from django.core.exceptions import ValidationError
from .models import Item


class ItemService:
    @staticmethod
    def check_cycle(item, new_parent):
        actual = new_parent
        while actual:
            if actual.id == item.id:
                return True
            actual = actual.padre
        return False

    @staticmethod
    def move_item(item, new_parent):
        if ItemService.check_cycle(item, new_parent):
            raise ValidationError("No puedes crear ciclos")

        item.padre = new_parent
        item.save()
        return item

    @staticmethod
    def create_item(user, data, file=None):
        item = Item(usuario=user, **data)

        if item.tipo == Item.Tipo.CARPETA:
            item.ruta = None
            item.tamano_bytes = None
            item.mime_type = None
        else:
            if not file:
                raise ValidationError("Archivo requerido")

            item.ruta = f"uploads/{user.id}/{file.name}"
            item.tamano_bytes = file.size
            item.mime_type = file.content_type

        item.save()
        return item
