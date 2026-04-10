#!/bin/bash
set -e

APP_DIR="/app"
cd "$APP_DIR"

# Instalar dependencias
pip install --no-cache-dir --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -r requirements.txt
else
    pip install --no-cache-dir django djangorestframework django-cors-headers psycopg[binary,pool] djangorestframework-simplejwt
    # Guardar el estado de las dependencias
    pip freeze > requirements.txt
fi

# Crear proyecto Django si no existe
if [ ! -f "manage.py" ]; then
    echo "Creando un proyecto Django completo..."
    django-admin startproject myproject .
fi

# Limpiado
rm -rf db.sqlite3

# Arrancar Django
echo "Arrancando Django..."
exec python manage.py runserver 0.0.0.0:8000