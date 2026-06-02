#!/bin/bash
echo "🛠️ Preparando contorna local para o meu proxecto..."

VENV_DIR="backend/libraries"
HASH_FILE="backend/.pip_hash_local"
REQUIREMENTS="backend/requirements.txt"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip

if [ -f "$REQUIREMENTS" ]; then
    CURRENT_HASH=$(md5sum "$REQUIREMENTS" | cut -d' ' -f1)
    STORED_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "")

    if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
        echo "📦 Dependencias actualizadas, instalando en entorno local..."
        pip install --no-cache-dir -r "$REQUIREMENTS"
        echo "$CURRENT_HASH" > "$HASH_FILE"
    else
        echo "✅ Dependencias locais sen cambios, saltando pip install."
    fi
else
    echo "⚠️  Non se atopou requirements.txt en backend/. Executa primeiro init-backend.sh."
fi

echo "🚀 Todo preparado!"
