from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

#Creamos el router
router = DefaultRouter()
#Registramos el ViewSet
router.register(r'', ItemViewSet, basename='item')

#Incluimos la ruta
urlpatterns = [
    path('', include(router.urls)),
]