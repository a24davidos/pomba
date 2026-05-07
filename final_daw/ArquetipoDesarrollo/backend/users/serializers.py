from rest_framework import serializers
from django.contrib.auth import get_user_model 
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    #Evito que se devuelva en el JSON de respuesta
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "nombre", "apellidos", "foto_perfil")

    def validate_password(self, value):
        try:
            #Validamos la contraseña
            validate_password(value)
        except exceptions.ValidationError as e:
            #Mandamos error si hay algún problema
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self,validated_data):
        user = User.objects.create_user(**validated_data)
        
        return user
    