from rest_framework import serializers
from django.contrib.auth import get_user_model 

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    #Evito que se devuelva en el JSON de respuesta
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "nombre", "apellidos", "foto_perfil")

    def create(self,validated_data):
        user = User.objects.create_user(**validated_data)
        
        return user
    