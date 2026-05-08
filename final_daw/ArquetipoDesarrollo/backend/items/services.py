# services.py
from django.core.exceptions import ValidationError


class ItemService:
    @staticmethod
    def check_cycle(item, new_parent):
        """
        Retorna True si mover 'item' bajo 'new_parent' crearía un bucle infinito.
        """
        if not item or not new_parent:
            return False

        actual = new_parent
        while actual:
            if actual.id == item.id:
                return True
            actual = actual.padre
        return False

    @staticmethod
    def validar_movimiento(item, nuevo_padre):
        """
        Agrupa varias reglas de negocio para mover archivos.
        """
        if ItemService.check_cycle(item, nuevo_padre):
            raise ValidationError(
                "No puedes mover una carpeta dentro de sí misma o de sus subcarpetas."
            )

        # Aquí podrías añadir más reglas en el futuro, ej:
        # if nuevo_padre.espacio_disponible < item.tamano: ...
