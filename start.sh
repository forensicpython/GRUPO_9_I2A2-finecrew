#!/bin/bash

echo "🚀 Iniciando FinaCrew no Railway..."

# Verificar se o build do React existe
if [ ! -d "frontend/build" ]; then
    echo "❌ Build do React não encontrado!"
    echo "Execute: cd frontend && npm run build"
    exit 1
fi

# Criar diretórios necessários
mkdir -p uploads temp_data output

# Iniciar a aplicação
echo "✅ Iniciando servidor Flask..."
python -m gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 api.app:app