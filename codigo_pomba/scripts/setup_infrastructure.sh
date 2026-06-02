#!/bin/bash
set -e

echo "⏳ Esperando a que Garage (v2) estea dispoñible..."

# 1. Esperar a que o servizo responda
until docker exec garage /garage status > /dev/null 2>&1; do
  sleep 2
done

echo "✅ Garage responde"

# 2. Obter Node ID real
echo "📌 Obteniendo Node ID..."
NODE_ID=$(docker exec garage /garage node id | grep -Eo '[a-f0-9]{64}' | head -n 1)

if [ -z "$NODE_ID" ]; then
  echo "❌ Non se puido obter Node ID"
  exit 1
fi

echo "📌 Node ID: $NODE_ID"

# 3. Aplicar layout
echo "🏗️ Configurando layout..."

# Asignar nodo
docker exec garage /garage layout assign "$NODE_ID" --zone dc1 --capacity 1G

# Buscamos a versión na liña de suxestión de comando "apply --version X"
LAYOUT_VERSION=$(docker exec garage /garage layout show | grep "apply --version" | grep -Eo '[0-9]+' | tail -n 1)

if [ -z "$LAYOUT_VERSION" ] || [ "$LAYOUT_VERSION" = "0" ]; then
    LAYOUT_VERSION="1"
fi

echo "📌 Aplicando layout version: $LAYOUT_VERSION"
# Si el layout ya se aplicó antes, este comando simplemente no hará nada o confirmará, 
# pero le ponemos un || true por si acaso para que el script no se detenga si ya está aplicado.
docker exec garage /garage layout apply --version "$LAYOUT_VERSION" || echo "Layout ya aplicado."

echo "⏳ Esperando estabilización..."
sleep 3

# 4. Crear key si no existe
if ! docker exec garage /garage key list | grep -q "django-key"; then
  echo "🔑 Creando API key..."

  docker exec garage /garage key create django-key > /tmp/key.txt

  ACCESS_KEY=$(grep "Key ID:" /tmp/key.txt | awk '{print $3}')
  SECRET_KEY=$(grep "Secret key:" /tmp/key.txt | awk '{print $3}')

  echo "AWS_ACCESS_KEY_ID=$ACCESS_KEY"
  echo "AWS_SECRET_ACCESS_KEY=$SECRET_KEY"

  ENV_PATH="./Docker/.env"

  sed -i "" "s/^AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$ACCESS_KEY/" "$ENV_PATH"
  sed -i "" "s/^AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$SECRET_KEY/" "$ENV_PATH"
fi

# 5. Crear bucket
echo "📦 Creando bucket..."
# En v2, si el bucket ya existe, el comando falla, así que comprobamos antes
if ! docker exec garage /garage bucket list | grep -q "mi-bucket-app"; then
    docker exec garage /garage bucket create mi-bucket-app
fi

echo "🔐 Aplicando permisos..."

docker exec garage /garage bucket allow mi-bucket-app --key django-key --read --write

echo "🚀 Garage v2 listo e operativo"