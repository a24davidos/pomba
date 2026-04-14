import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

def subir_imagen(instance, filename):
    ext = filename.split('.')[-1]
    nombre_unico = f"{uuid.uuid4()}.{ext}"
    fecha_path = now().strftime("%Y/%m")
    return os.path.join('avatares', fecha_path, nombre_unico)

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(max_length=150,unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellidos = models.CharField(max_length=100, null=True, blank=True)
    foto_perfil = models.ImageField(upload_to=subir_imagen, null=True, blank=True)

    #Quito campos que no utilizare
    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    #Como el campo Usuario no lo vamos a utilizar, lo copiamos siempre del email.
    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email