from .base import *
import os

# --- VARIABLES DE ENTORNO ---
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-insecure-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']

# --- DATABASE (POSTGRESQL) ---
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

# --- ELASTICSEARCH ---
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
    },
}

# --- CONFIGURACIÓN DE GARAGE (S3 STORAGE PARA MEDIA) ---
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'mi-bucket-app')

# En desarrollo, si accedes desde fuera del contenedor (browser del Mac), 
# usa http://localhost:3900. Si todo va por Nginx, usa el endpoint del proxy.
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'http://localhost:3900')

# Configuración necesaria para Garage v2
AWS_S3_REGION_NAME = 'garage'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None  # Garage v2 prefiere manejar permisos vía bucket allow

# IMPORTANTE: Forzamos el estilo de ruta para evitar problemas de DNS con el nombre del bucket
AWS_S3_ADDRESSING_STYLE = "path"

# Configuramos para que SOLO los archivos multimedia suban a Garage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = "/media/"

# --- STATIC FILES (LOCAL EN DESARROLLO) ---
# Se mantienen en el sistema de archivos local, servidos por Nginx
STATIC_URL = '/static_backend/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True