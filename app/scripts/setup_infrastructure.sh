#!/bin/bash
# Configura Garage (S3) por primera vez: layout, clave de acceso y bucket.

# Variables opcionales:
#   GARAGE_CONTAINER  nombre del contenedor (por defecto: garage)
#   ENV_FILE          fichero donde se guardan las claves (por defecto: Docker/.env.development)
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GARAGE_CONTAINER="${GARAGE_CONTAINER:-garage}"
ENV_FILE="${ENV_FILE:-$APP_DIR/Docker/.env.development}"
BUCKET="pomba-app"
KEY_NAME="django-app"

garage() {
  docker exec "$GARAGE_CONTAINER" /garage "$@" 2>/dev/null
}

# Sustituye (o añade) VARIABLE=valor en el fichero .env, de forma portable (macOS y Linux)
set_env() {
  local var="$1" value="$2" tmp
  tmp="$(mktemp)"
  VAR="$var" VALUE="$value" awk '
    BEGIN { FS = OFS = "="; done = 0 }
    $1 == ENVIRON["VAR"] { print ENVIRON["VAR"] "=" ENVIRON["VALUE"]; done = 1; next }
    { print }
    END { if (!done) print ENVIRON["VAR"] "=" ENVIRON["VALUE"] }
  ' "$ENV_FILE" > "$tmp"
  cat "$tmp" > "$ENV_FILE"   # cat conserva permisos del original
  rm -f "$tmp"
}

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ No existe $ENV_FILE. Cópialo primero desde Docker/.env.example."
  exit 1
fi

echo "⏳ Esperando a que Garage esté disponible..."
until garage status > /dev/null; do
  sleep 2
done
echo "✅ Garage responde"

# 1. Layout: solo si el nodo todavía no tiene rol
LAYOUT_VERSION="$(garage layout show | sed -n 's/^Current cluster layout version: *//p')"
if [ "${LAYOUT_VERSION:-0}" = "0" ]; then
  NODE_ID="$(garage node id | grep -Eo '[a-f0-9]{64}' | head -n 1)"
  if [ -z "$NODE_ID" ]; then
    echo "❌ No se pudo obtener el Node ID"
    exit 1
  fi
  echo "🏗️  Configurando layout (nodo ${NODE_ID:0:16}...)"
  garage layout assign "$NODE_ID" --zone dc1 --capacity 1G > /dev/null
  garage layout apply --version 1 > /dev/null
  sleep 3
else
  echo "✅ Layout ya aplicado (versión $LAYOUT_VERSION)"
fi

# 2. Bucket
if garage bucket info "$BUCKET" > /dev/null; then
  echo "✅ Bucket $BUCKET ya existe"
else
  echo "📦 Creando bucket $BUCKET..."
  garage bucket create "$BUCKET" > /dev/null
fi

# 3. Clave de acceso (el secreto solo se puede ver al crearla)
if garage key info "$KEY_NAME" > /dev/null; then
  echo "✅ Clave $KEY_NAME ya existe: no se toca $ENV_FILE"
  echo "   (si perdiste el secreto: garage key delete $KEY_NAME y vuelve a ejecutar)"
else
  echo "🔑 Creando clave $KEY_NAME..."
  KEY_OUTPUT="$(garage key create "$KEY_NAME")"
  ACCESS_KEY="$(echo "$KEY_OUTPUT" | awk '/Key ID:/ {print $3}')"
  SECRET_KEY="$(echo "$KEY_OUTPUT" | awk '/Secret key:/ {print $3}')"
  if [ -z "$ACCESS_KEY" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ No se pudieron leer las claves de la salida de Garage"
    exit 1
  fi
  set_env AWS_ACCESS_KEY_ID "$ACCESS_KEY"
  set_env AWS_SECRET_ACCESS_KEY "$SECRET_KEY"
  set_env AWS_STORAGE_BUCKET_NAME "$BUCKET"
  echo "✅ Claves guardadas en $ENV_FILE"
fi

# 4. Permisos de la clave sobre el bucket
garage bucket allow --read --write "$BUCKET" --key "$KEY_NAME" > /dev/null
echo "🚀 Garage listo y operativo"
