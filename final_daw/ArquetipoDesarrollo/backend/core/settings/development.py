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

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "mi-bucket-app")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", "http://garage:3900")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "garage")

AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "addressing_style": "path",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_URL = "/static_backend/"
STATIC_ROOT = BASE_DIR / "staticfiles"

LANGUAGE_CODE = "es-ES"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True