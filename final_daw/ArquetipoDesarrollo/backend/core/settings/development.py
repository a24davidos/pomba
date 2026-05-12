from .base import *
import os


# =========================================================
# SEGURIDAD / CONFIG GENERAL
# =========================================================

# Clave secreta de Django (NO usar fallback en producción)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Debug controlado por variable de entorno
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# En producción deberías restringir esto
ALLOWED_HOSTS = ['*']


# =========================================================
# BASE DE DATOS (POSTGRESQL)
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# =========================================================
# ELASTICSEARCH (búsqueda avanzada)
# =========================================================

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': os.environ.get(
            'ELASTICSEARCH_URL',
            'http://elasticsearch:9200'
        )
    },
}


# =========================================================
# GARAGE (S3 COMPATIBLE STORAGE)
# =========================================================
# Aquí conectas Django con Garage (S3 API compatible)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Bucket donde se almacenan los archivos
AWS_STORAGE_BUCKET_NAME = os.environ.get(
    'AWS_STORAGE_BUCKET_NAME',
    'mi-bucket-app'
)

# Endpoint interno del cluster Docker (Garage)
AWS_S3_ENDPOINT_URL = os.environ.get(
    'AWS_S3_ENDPOINT_URL',
    'http://garage:3900'
)

# Región ficticia (Garage no usa AWS real)
AWS_S3_REGION_NAME = 'garage'

# Firma S3 estándar
AWS_S3_SIGNATURE_VERSION = 's3v4'

# =========================================================
# COMPORTAMIENTO DE ARCHIVOS
# =========================================================

# No sobrescribir archivos con mismo nombre
AWS_S3_FILE_OVERWRITE = False

# Sin permisos públicos automáticos (IMPORTANTE para seguridad)
AWS_DEFAULT_ACL = None

# Usar rutas estilo /bucket/key (OBLIGATORIO en Garage)
AWS_S3_ADDRESSING_STYLE = "path"

# Desactivar SSL en entorno local
AWS_S3_USE_SSL = False
AWS_S3_VERIFY = False


# =========================================================
# STORAGE BACKEND (MEDIA EN S3 / GARAGE)
# =========================================================

# Django usará S3 como almacenamiento principal de archivos
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# URL base de archivos (usada solo si necesitas referencia directa)
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"

# URLs firmadas (tipo Google Drive)
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600  # 1 hora


# =========================================================
# STATIC FILES (FRONTEND BACKEND)
# =========================================================

STATIC_URL = '/static_backend/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True