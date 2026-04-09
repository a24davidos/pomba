#!/bin/bash
set -e

APP_DIR="/app"
cd "$APP_DIR"

# Creo e activo o entorno virtual
python3 -m venv libraries
source libraries/bin/activate

# Instalación de dependencias
pip install django psycopg2

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 3. Gardar o estado das librerías
pip freeze > requirements.txt

# 4. Crear o proxecto se non existe
if [ ! -f "manage.py" ]; then
    echo "Creando un proxecto Django completo..."
    django-admin startproject myproject .
fi


# 5. Arrancar Django
echo "Arrancando Django..."
exec python manage.py runserver 0.0.0.0:8000