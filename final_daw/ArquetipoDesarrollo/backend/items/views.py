from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Exists, OuterRef

from .models import Item
from .serializers import ItemSerializer
from .services import ItemService


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer

    # Filtramos que el usuario solo pueda trabajar sobre el queryset que le pertenece
    def get_queryset(self):
        hijos = Item.objects.filter(padre=OuterRef("pk"), eliminado=False)

        qs = Item.objects.filter(usuario=self.request.user)

        carpeta_id = self.request.query_params.get("carpeta")
        es_papelera = self.request.query_params.get("papelera") == "true"

        if es_papelera:
            qs = qs.filter(eliminado=True)

        elif carpeta_id:
            qs = qs.filter(padre_id=carpeta_id, eliminado=False)

        else:
            qs = qs.filter(padre__isnull=True, eliminado=False)

        return qs.annotate(tiene_hijos=Exists(hijos)).order_by("-tipo", "nombre")
    
    def list(self, request, *args, **kwargs):
        """
        Sobrescribimos list para devolver los items Y el breadcrumb en una sola petición.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        carpeta_id = request.query_params.get("carpeta")
        
        return Response({
            "items": serializer.data,
            "breadcrumb": self._get_breadcrumb(carpeta_id)
        })

    def _get_breadcrumb(self, carpeta_id):
        """
        Calcula la ruta desde la raíz hasta la carpeta actual.
        """
        ruta = [{"id": None, "label": "Inicio"}]
        
        if not carpeta_id:
            return ruta

        try:
            # Buscamos la carpeta actual del usuario
            actual = Item.objects.get(id=carpeta_id, usuario=self.request.user, tipo='carpeta')
            nodos_padre = []
            
            # Bucle para subir por el árbol de carpetas
            curr = actual
            while curr is not None:
                nodos_padre.append({
                    "id": curr.id,
                    "label": curr.nombre
                })
                curr = curr.padre
            
            # Invertimos para que vaya de Raíz -> Carpeta Actual
            ruta.extend(reversed(nodos_padre))
            
        except (Item.DoesNotExist, ValueError):
            # Si el ID no existe o es inválido, devolvemos solo el Inicio
            pass
            
        return ruta

    # CREATE (delegado a service)
    def perform_create(self, serializer):
        # Cogemos el archivo de la request
        blob = self.request.FILES.get("file")

        # Se lo pasamos al service como 'fichero'
        item = ItemService.crear_item(
            usuario=self.request.user, 
            datos=serializer.validated_data, 
            fichero=blob 
        )
        serializer.instance = item

    # =========================================================
    # ACTIONS
    # =========================================================

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        """
        TODO: mover item a otra carpeta
        """
        #Sino uso self, estaría ignorando el queryset, y haciendo una consulta directa a la base de datos por lo tanto me saltaría toda protección posible
        item = self.get_object()


        pass

    @action(detail=True, methods=["post"])
    def rename(self, request, pk=None):
        """
        TODO: renombrar item
        """
        pass

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk=None):
        """
        TODO: marcar/desmarcar favorito
        """
        pass

    @action(detail=True, methods=["post"])
    def trash(self, request, pk=None):
        """
        TODO: mover a papelera
        """
        pass

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """
        TODO: restaurar de papelera
        """
        pass
