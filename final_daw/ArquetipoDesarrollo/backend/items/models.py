from django.db import models
from users.models import User
from django.core.exceptions import ValidationError


# Create your models here.
class Item(models.Model):
    class Tipo(models.TextChoices):
        ARCHIVO = "archivo", "Archivo"
        CARPETA = "carpeta", "Carpeta"

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    padre = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="hijos"
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")

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

    # --- Datetime ---
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def clean(self):
        # Lógica anti-ciclos: no puedes ser padre de ti mismo ni de tus hijos
        if self.padre and self.id:
            actual = self.padre
            while actual:
                if actual.id == self.id:
                    raise ValidationError("No puedes crear ciclos en la jerarquía.")
                actual = actual.padre

    # Controlo que al crear una carpeta no se guarden, rutas, ni tamaño de bytes, ni el mime
    def save(self, *args, **kwargs):

        if self.tipo == self.Tipo.CARPETA:
            self.ruta = None
            self.tamano_bytes = None
            self.mime_type = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        constraints = [
            # Regla para cuando hay un padre (subcarpetas)
            models.UniqueConstraint(
                fields=["usuario", "padre", "nombre", "eliminado"],
                name="unique_nombre_en_carpeta",
                condition=models.Q(padre__isnull=False),
            ),
            #  Regla para cuando NO hay padre (raíz)
            models.UniqueConstraint(
                fields=["usuario", "nombre", "eliminado"],
                name="unique_nombre_en_raiz",
                condition=models.Q(padre__isnull=True),
            ),
        ]

        indexes = [
            # Indice para los archivos de cada usuario
            models.Index(fields=["usuario"], name="idx_items_usuario"),
            # Indice para los hijos de la carpeta
            models.Index(fields=["padre"], name="idx_items_padre"),
            # Índice para filtrar archivos/carpetas por usuario y carpeta
            models.Index(fields=["usuario", "padre"], name="idx_items_usuario_padre"),
            # Indice papelera
            models.Index(fields=["usuario", "eliminado"], name="idx_items_eliminado"),
        ]
