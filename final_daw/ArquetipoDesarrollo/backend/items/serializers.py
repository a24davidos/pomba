from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    tiene_hijos = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'nombre', 'tipo', 'padre', 'usuario',
            'ruta', 'tamano_bytes', 'mime_type',
            'metadatos', 'favorito', 'eliminado',
            'fecha_eliminado', 'fecha_creacion', 'fecha_modificacion', 'tiene_hijos'
        ]
        read_only_fields = [
            'id', 'usuario',
            'fecha_creacion', 'tamano_bytes', 'mime_type'
        ]

    def get_tiene_hijos(self, obj):
        return getattr(obj, 'tiene_hijos', False)

    def validate_padre(self, value):
        if value is not None:
            if value.tipo != Item.Tipo.CARPETA:
                raise serializers.ValidationError(
                    "El elemento padre debe ser una carpeta"
                )

            if value.eliminado:
                raise serializers.ValidationError(
                    "No puedes usar un elemento eliminado como padre"
                )

        return value

    def validate(self, data):
        tipo = data.get('tipo', self.instance.tipo if self.instance else None)

        if tipo == Item.Tipo.ARCHIVO:
            ruta = data.get('ruta') or (self.instance.ruta if self.instance else None)
            if not ruta:
                raise serializers.ValidationError({
                    'ruta': 'Un archivo requiere una ruta de almacenamiento'
                })

        return data