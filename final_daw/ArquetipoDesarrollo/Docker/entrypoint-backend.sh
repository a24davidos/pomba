#!/bin/bash
set -e

APP_DIR="/app"
cd "$APP_DIR"

# Instalar dependencias básicas
pip install --no-cache-dir --upgrade pip
pip install django djangorestframework django-cors-headers psycopg[binary,pool] djangorestframework-simplejwt

# Instalar dependencias adicionales si existe requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Guardar el estado de las dependencias
pip freeze > requirements.txt

# Crear proyecto Django si no existe
if [ ! -f "manage.py" ]; then
    echo "Creando un proyecto Django completo..."
    django-admin startproject myproject .
fi

# Arrancar Django
echo "Arrancando Django..."
exec python manage.py runserver 0.0.0.0:8000