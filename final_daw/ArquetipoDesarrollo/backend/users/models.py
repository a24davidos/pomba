import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now

def subir_imagen(instance, filename):
    ext = filename.split('.')[-1].lower()
    return os.path.join('avatares', now().strftime("%Y/%m"), f"{uuid.uuid4()}.{ext}")

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)
    
# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=150)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to=subir_imagen, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email


class Item(models.Model):
    class Tipo(models.TextChoices):
        ARCHIVO = 'archivo', 'Archivo'
        CARPETA = 'carpeta', 'Carpeta'

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices
    )
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hijos'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # --- STORAGE (SOLO ARCHIVOS) ---
    ruta = models.CharField(max_length=1024, null=True, blank=True, db_index=True)
    tamano_bytes = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, null=True, blank=True)

    # --- METADATOS ---
    metadatos = models.JSONField(default=dict, blank=True)

    favorito = models.BooleanField(default=False)

    # --- PAPELERA (SOFT DELETE) ---
    eliminado = models.BooleanField(default=False)
    fecha_eliminado = models.DateTimeField(null=True, blank=True)

    # --- TIMESTAMPS ---
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # Controlo que al crear una carpeta no se guarden, rutas, ni tamaño de bytes, ni el mime
    def save(self, *args, **kwargs):
        if self.tipo == self.Tipo.CARPETA:
            self.ruta = None
            self.tamano_bytes = None
            self.mime_type = None
        
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            # Regla para cuando hay un padre (subcarpetas)
            models.UniqueConstraint(
                fields=['usuario', 'padre', 'nombre', 'eliminado'],
                name='unique_nombre_en_carpeta',
                condition=models.Q(padre__isnull=False)
            ),
            #  Regla para cuando NO hay padre (raíz)
            models.UniqueConstraint(
                fields=['usuario', 'nombre', 'eliminado'],
                name='unique_nombre_en_raiz',
                condition=models.Q(padre__isnull=True)
            ),
        ]

        indexes = [
            #Indice para los archivos de cada usuario
            models.Index(fields=['usuario'], name='idx_items_usuario'),
            #Indice para los hijos de la carpeta
            models.Index(fields=['padre'], name='idx_items_padre'),
            # Índice para filtrar archivos/carpetas por usuario y carpeta
            models.Index(fields=['usuario', 'padre'], name='idx_items_usuario_padre'),
            #Indice papelera
            models.Index(fields=['usuario', 'eliminado'], name='idx_items_eliminado')
        ]

#NOTA PARA MI MISMO, CUANDO QUIERA CONSEGUIR LAS RUTAS, HACER UNA UNICA LLAMADA A LA BD, CARGAR EN MEMORIA Y DE MANERA RECURSIVA CONSEGUIR LOS PARENTS ETCCC