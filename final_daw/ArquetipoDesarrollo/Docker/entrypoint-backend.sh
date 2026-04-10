#!/bin/bash
set -e

APP_DIR="/app"
cd "$APP_DIR"

# 1. Actualizar pip
pip install --no-cache-dir --upgrade pip

# 2. Lógica de instalación y FREEZE
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando desde requirements.txt existente..."
    pip install --no-cache-dir -r requirements.txt
else
    echo "📝 No hay requirements.txt. Instalando base y generando archivo..."
    # Instalamos tu stack tecnológico
    pip install django \
                djangorestframework \
                django-cors-headers \
                "psycopg[binary,pool]" \
                djangorestframework-simplejwt \
                Pillow
fi

# 3. Crear proyecto Django si la carpeta está vacía
if [ ! -f "manage.py" ]; then
    echo "🔨 Creando nuevo proyecto Django..."
    django-admin startproject myproject .
fi

# 4. Limpieza (opcional, como tenías antes)
rm -rf db.sqlite3

# 5. Arrancar
echo "🚀 Arrancando Django..."
exec python manage.py runserver 0.0.0.0:8000