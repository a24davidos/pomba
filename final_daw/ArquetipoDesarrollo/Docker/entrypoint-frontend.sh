#!/bin/bash
set -e

APP_DIR="/app"

cd "$APP_DIR"

#Creo o proxecto se non existe
if [ ! -f "package.json" ]; then
    echo "Creando un proxecto vue.js completo..."
    npm create vite@latest . -- --template vue
fi

#Instalo as dependencias
npm install
rm -rf .vscode/ .gitignore

#Arranco vue
echo "Arrancando Vue.js..."
npm run dev -- --host 0.0.0.0 --port 5173