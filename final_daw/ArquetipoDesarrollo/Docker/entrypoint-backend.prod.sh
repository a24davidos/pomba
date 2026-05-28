#!/bin/bash
set -e

cd /app

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recopilando ficheros estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
