from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Exists, OuterRef

from .models import Item
from .serializers import ItemSerializer
from .services import ItemService


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer

    # Filtramos que el usuario solo pueda trabajar sobre el queryset que le pertenece
    def get_queryset(self):
        user = self.request.user

        # 1.- Cogemos los Items del usuario
        qs = Item.objects.filter(usuario=user)

        # 2.- Captura de parámetros
        carpeta_id = self.request.query_params.get("carpeta")
        es_papelera = self.request.query_params.get("papelera") == "true"
        es_favorito = self.request.query_params.get("favorito") == "true"
        
        # 3.- Aplicación de filtros (Lógica de negocio)
        if es_papelera:
            #Eliminados
            qs = qs.filter(eliminado=True)
            # Favoritos
        elif es_favorito:
            qs = qs.filter(favorito=True, eliminado=False)
        else:
            # Mi unidad
            qs = qs.filter(eliminado=False)

        # 4.- Navegación por carpetas (independiente del modo)
        if carpeta_id:
            qs = qs.filter(padre_id=carpeta_id)
        elif not es_papelera and not es_favorito:
            # Si no hay carpeta y es modo normal, mostramos la raíz
            qs = qs.filter(padre__isnull=True)

        hijos = Item.objects.filter(padre=OuterRef("pk"), eliminado=False)
        return qs.annotate(tiene_hijos=Exists(hijos)).order_by("-tipo", "nombre")
    

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        carpeta_id = request.query_params.get("carpeta")
        
        breadcrumb = ItemService.obtener_breadcrumb(request.user, carpeta_id)
        
        return Response({
            "items": serializer.data,
            "breadcrumb": breadcrumb
        })


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

    
    @action(detail=False, methods=["post"])
    def trash(self, request):
        """
        Función para mandar a la papelera (Soft Delete)
        """
        ids = request.data.get("ids", [])

        if not ids:
            return Response(
                {"detail": "No se han enviado elementos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cantidad = ItemService.mover_a_papelera(
                ids=ids,
                usuario=request.user
            )
            return Response({
                "detail": f"Se han movido {cantidad} elementos a la papelera"
            })

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """
        TODO: restaurar de papelera
        """
        pass
