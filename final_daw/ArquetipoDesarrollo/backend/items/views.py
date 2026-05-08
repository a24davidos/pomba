from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

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

    # CREATE (delegado a service)
    def perform_create(self, serializer):
        file_obj = self.request.FILES.get("file")

        item = ItemService.crear_item(
            user=self.request.user, data=serializer.validated_data, file=file_obj
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
