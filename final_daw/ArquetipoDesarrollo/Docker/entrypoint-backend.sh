#!/bin/bash
set -e

APP_DIR="/app"
cd "$APP_DIR"

# Crear y activar entorno virtual
python3 -m venv libraries
source libraries/bin/activate

# Instalar dependencias básicas
pip install django psycopg2-binary boto3

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