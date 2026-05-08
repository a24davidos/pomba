from rest_framework import serializers
from .models import Item
from .services import ItemService


class ItemSerializer(serializers.ModelSerializer):
    tiene_hijos = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "nombre",
            "tipo",
            "padre",
            "usuario",
            "ruta",
            "tamano_bytes",
            "mime_type",
            "metadatos",
            "favorito",
            "eliminado",
            "fecha_eliminado",
            "fecha_creacion",
            "fecha_modificacion",
            "tiene_hijos",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "fecha_creacion",
            "tamano_bytes",
            "mime_type",
        ]

    # -------------------
    # output
    # -------------------
    def get_tiene_hijos(self, obj):
        return getattr(obj, "tiene_hijos", False)

    # -------------------
    # validaciones simples
    # -------------------
    def validate_tipo(self, value):
        if self.instance and self.instance.tipo != value:
            raise serializers.ValidationError(
                "No se puede cambiar el tipo de un elemento existente."
            )
        return value

    def validate_padre(self, value):
        if value is None:
            return value

        if value.tipo != Item.Tipo.CARPETA:
            raise serializers.ValidationError("El elemento padre debe ser una carpeta.")

        if value.eliminado:
            raise serializers.ValidationError(
                "No puedes mover elementos a una carpeta eliminada."
            )

        if self.instance:
            try:
                ItemService.validar_movimiento(self.instance, value)
            except Exception as e:
                raise serializers.ValidationError(str(e))

        return value

    # -------------------
    # validación cruzada
    # -------------------
    def validate(self, data):
        tipo = data.get("tipo", self.instance.tipo if self.instance else None)
        ruta = data.get("ruta", self.instance.ruta if self.instance else None)

        if tipo == Item.Tipo.ARCHIVO and not ruta:
            raise serializers.ValidationError(
                {"ruta": "Un archivo requiere una ruta de almacenamiento."}
            )

        return data
