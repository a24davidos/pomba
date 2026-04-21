from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer

# Create your views here.
class RegisterView(generics.CreateAPIView):
    """
    Esta vista maneja exclusivamente la creación de usuarios (POST).
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]