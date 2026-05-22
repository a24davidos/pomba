from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    ProfilePhotoSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Registro de nuevos usuarios."""
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    GET    → devuelve el perfil del usuario autenticado.
    PATCH  → actualiza nombre, apellidos o email.
    DELETE → elimina la cuenta del usuario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializador = UserProfileSerializer(request.user, context={"request": request})
        return Response(serializador.data)

    def patch(self, request):
        serializador = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response(UserProfileSerializer(request.user, context={"request": request}).data)

    def delete(self, request):
        usuario = request.user
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    """POST → cambia la contraseña del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializador = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializador.is_valid(raise_exception=True)
        request.user.set_password(serializador.validated_data["password_nuevo"])
        request.user.save()
        return Response({"detail": "Contraseña actualizada correctamente."})


class ProfilePhotoView(APIView):
    """POST → sube o reemplaza la foto de perfil del usuario (guardada en Garage/S3)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user

        # Eliminar la foto anterior de S3 si existe
        if usuario.foto_perfil:
            try:
                usuario.foto_perfil.delete(save=False)
            except Exception:
                pass

        serializador = ProfilePhotoSerializer(usuario, data=request.data, partial=True)
        serializador.is_valid(raise_exception=True)
        serializador.save()

        url_foto = None
        if usuario.foto_perfil:
            try:
                url_foto = usuario.foto_perfil.url
            except Exception:
                pass

        return Response({"foto_perfil_url": url_foto}, status=status.HTTP_200_OK)
