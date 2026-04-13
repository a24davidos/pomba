#!/bin/bash
set -e

APP_DIR="/app"
PROJECT_NAME=${PROJECT_NAME:-myproject} # Usamos un valor por defecto si no está definida

cd "$APP_DIR"

if [ ! -f "Makefile" ] || [ ! -f "requirements.txt" ]; then
    cp /usr/Makefile "$APP_DIR"/Makefile 2>/dev/null || true
    cp -n /usr/requirements.txt "$APP_DIR"/requirements.txt 2>/dev/null || true
fi

echo "📦 Instalando dependencias do stack..."
pip install --no-cache-dir --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -r requirements.txt
else
    pip install django \
                djangorestframework \
                django-cors-headers \
                "psycopg[binary,pool]" \
                djangorestframework-simplejwt \
                boto3 \
                django-storages \
                elasticsearch \
                django-elasticsearch-dsl
fi

# Crear proyecto Django si no existe
if [ ! -f "manage.py" ]; then
    echo "🔨 Creando proxecto Django: $PROJECT_NAME..."
    django-admin startproject "$PROJECT_NAME" .
fi


echo "⚙️ Configurando a estrutura do proxecto..."
cd "$APP_DIR/$PROJECT_NAME"

if [ -f "settings.py" ]; then
    echo "📦 Creando os settings personalizados..."
    rm -f db.sqlite3
    mkdir -p settings
    touch ./settings/development.py ./settings/__init__.py
    mv settings.py settings/base.py
    
    # Actualizamos los archivos para que apunten a settings.development
    sed -i "s/$PROJECT_NAME.settings/$PROJECT_NAME.settings.development/g" "$APP_DIR/manage.py"
    sed -i "s/$PROJECT_NAME.settings/$PROJECT_NAME.settings.development/g" "$APP_DIR/$PROJECT_NAME/wsgi.py"
    sed -i "s/$PROJECT_NAME.settings/$PROJECT_NAME.settings.development/g" "$APP_DIR/$PROJECT_NAME/asgi.py"

    # Limpa o base.py e engade un .parent
    cat <<EOF > "$APP_DIR/$PROJECT_NAME/settings/base.py"
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Aplicacións instaladas
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    # Aquí podes engadir as túas aplicacións locais
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'storages',
    'django_elasticsearch_dsl',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Orixes permitidos para desenvolvemento (Adaptado para Vue 3 / Vite)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

ROOT_URLCONF = '$PROJECT_NAME.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = '$PROJECT_NAME.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
EOF

    # Crea o novo development.py adaptado ao stack
    cat <<EOF > "$APP_DIR/$PROJECT_NAME/settings/development.py"
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
        'NAME': os.environ.get('DB_NAME', 'mydb'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'abc123.'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Configuración de Elasticsearch
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://elasticsearch:9200'
    },
}

# Configuración de Garage (S3 Storage)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'mi-bucket-app')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'http://garage:3900')

# Forzamos usar S3_ENDPOINT_URL y no el por defecto de Amazon
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.garage.localhost:3900"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'

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
EOF
else
    echo "✅ Estrutura de settings configurada. Saltando paso..."
fi

echo "🔄 Aplicando migracións na base de datos..."
cd "$APP_DIR"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "🚀 Iniciando servidor de desenvolvemento..."
exec python manage.py runserver 0.0.0.0:8000