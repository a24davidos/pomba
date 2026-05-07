from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django.db.models import Exists, OuterRef
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer

    def get_queryset(self):
        # 1. Subquery para el atributo temporal
        hijos = Item.objects.filter(padre=OuterRef('pk'), eliminado=False)

        # 2. Filtro de seguridad base
        qs = Item.objects.filter(usuario=self.request.user)

        # 3. Capturamos los parámetros
        carpeta_id = self.request.query_params.get('carpeta') 
        es_papelera = self.request.query_params.get('papelera') == 'true'

        # 4. Lógica de navegación
        if es_papelera:
            qs = qs.filter(eliminado=True)
        elif carpeta_id:
            # Filtramos por el ID de la carpeta que nos pasa Vue
            qs = qs.filter(padre_id=carpeta_id, eliminado=False)
        else:
            # Si no hay carpeta_id, estamos en el nivel raíz
            qs = qs.filter(padre__isnull=True, eliminado=False)

        return qs.annotate(tiene_hijos=Exists(hijos)).order_by('-tipo', 'nombre')

    def perform_create(self, serializer):
        tipo = serializer.validated_data.get('tipo')

        # CASO CARPETA
        if tipo == Item.Tipo.CARPETA:
            serializer.save(
                usuario=self.request.user,
                ruta=None,
                tamano_bytes=None,
                mime_type=None
            )
        
        # CASO ARCHIVO
        else:
            file_obj = self.request.FILES.get('file')
            if not file_obj:
                raise ValidationError({"file": "No se ha proporcionado ningún archivo físico."})

            # Luego aqui tendre que cambiar cosas para trabajar con Garage
            # Por ahora guardamos los metadatos del archivo como un placeholder
            serializer.save(
                usuario=self.request.user,
                ruta=f"uploads/{self.request.user.id}/{file_obj.name}", # Un ejemplo de ruta
                tamano_bytes=file_obj.size,
                mime_type=file_obj.content_type,
                metadatos={"placeholder": "placeholder"}
            )