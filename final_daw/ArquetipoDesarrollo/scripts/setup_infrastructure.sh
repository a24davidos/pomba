#!/bin/bash
# scripts/setup_infrastructure.sh

echo "⏳ Agardando por Garage..."
until docker exec garage /garage status > /dev/null 2>&1; do
  sleep 2
done

# 1. Obter ID do nodo
NODE_ID=$(docker exec garage /garage status | grep -A 1 "ID" | tail -n 1 | awk '{print $1}')

# 2. Configurar Layout
# Na v0.8.2+, o comando apply necesita o número de versión (neste caso a 1)
if ! docker exec garage /garage layout show | grep -q "$NODE_ID"; then
    echo "🏗️ Configurando layout de Garage (dc1, capacity 1)..."
    docker exec garage /garage layout assign -z dc1 -c 1 "$NODE_ID"
    # Aplicamos a versión 1 especificamente
    docker exec garage /garage layout apply --version 1
    
    echo "📡 Agardando a que o nodo se estabilice..."
    sleep 5
fi

# 3. Xestionar chaves (key new)
if ! docker exec garage /garage key list | grep -q "django-key"; then
    echo "🔑 Xerando nova API Key..."
    # Reintentamos se hai problemas de quórum ao principio
    NEW_KEY=""
    while [ -z "$NEW_KEY" ]; do
        NEW_KEY=$(docker exec garage /garage key new --name django-key 2>/dev/null)
        if [ -z "$NEW_KEY" ]; then
            echo "🔄 Agardando quórum para crear chaves..."
            sleep 2
        fi
    done
    
    ACCESS_KEY=$(echo "$NEW_KEY" | grep "Key ID:" | awk '{print $3}')
    SECRET_KEY=$(echo "$NEW_KEY" | grep "Secret key:" | awk '{print $3}')
    
    ENV_PATH="./Docker/.env"
    
    if [ ! -z "$ACCESS_KEY" ]; then
        sed -i "" "s/^AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$ACCESS_KEY/" "$ENV_PATH"
        sed -i "" "s/^AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$SECRET_KEY/" "$ENV_PATH"
        echo "✅ Chaves gardadas en $ENV_PATH"
    fi
fi

# 4. Crear bucket e dar permisos
echo "📦 Asegurando bucket e permisos..."
# Agardamos quórum para o bucket
until docker exec garage /garage bucket create mi-bucket-app > /dev/null 2>&1; do
  sleep 2
done

docker exec garage /garage bucket allow --read --write mi-bucket-app --key django-key

echo "🚀 Infraestrutura de Garage lista e conectada!"