#!/bin/bash
echo "🛠️ Preparando contorna local para Musixest..."

if [ ! -d "backend/libraries" ]; then
    python3 -m venv backend/libraries
fi

source backend/libraries/bin/activate

echo "📦 Instalando dependencias para IDE..."
pip install --no-cache-dir --upgrade pip
if [ -f "backend/requirements.txt" ]; then
    pip install --no-cache-dir -r backend/requirements.txt
else
    pip install django djangorestframework django-cors-headers psycopg[binary,pool] djangorestframework-simplejwt
    pip freeze > backend/requirements.txt
fi

echo "🚀 Todo preparado!"