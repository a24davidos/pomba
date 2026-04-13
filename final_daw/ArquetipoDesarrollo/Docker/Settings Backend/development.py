from .base import *
import os

# Variables de contorna dende .env (Ajustado al nombre de tu variable)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-insecure-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*'] # En desarrollo, permitimos todo

# Database PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'), # Quitamos el 'abc123.'
        'HOST': os.environ.get('DB_HOST', 'db'),    # Aquí 'db' es el nombre del servicio en Docker, no es secreto
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Configuración de Elasticsearch
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://elasticsearch:9200'
    },
}

# --- Configuración de Garage (S3 Storage) ---
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'mi-bucket-app')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'http://garage:3900')

# Configuración para que las URLs sean accesibles desde tu navegador (Mac)
# Usamos localhost:3900 porque desde fuera de Docker entras por ahí
AWS_S3_CUSTOM_DOMAIN = f"localhost:3900/{AWS_STORAGE_BUCKET_NAME}"
AWS_S3_URL_PROTOCOL = 'http'

# Importante: Esto evita que Django use rutas relativas tipo "/archivo.txt"
AWS_QUERYSTRING_AUTH = False 
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'

# Forzamos a que las librerías no intenten usar firmas de AWS modernas que Garage no soporta
AWS_S3_SIGNATURE_VERSION = 's3v4'

# Configuramos para que los archivos multimedia suban a Garage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Internationalization
LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# Static files (Estáticos se sirven localmente en desarrollo)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://elasticsearch:9200',
        'retry_on_timeout': True,
    },
}