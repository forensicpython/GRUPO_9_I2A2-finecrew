#!/bin/bash

# Script para iniciar o ambiente de desenvolvimento FinaCrew
echo "🚀 Iniciando FinaCrew - Ambiente de Desenvolvimento"
echo "================================================="

# Verificar se está no diretório correto
if [ ! -f "api/app.py" ]; then
    echo "❌ Execute este script na pasta raiz do FinaCrew"
    exit 1
fi

# Função para verificar se uma porta está em uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Função para matar processos em portas específicas
kill_port() {
    local port=$1
    if check_port $port; then
        echo "🔄 Parando processo na porta $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Limpar portas se necessário
kill_port 3000
kill_port 5001

echo ""
echo "📋 Verificando dependências..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 primeiro."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale o Node.js primeiro."
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Instale o npm primeiro."
    exit 1
fi

echo "✅ Python3: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"

echo ""
echo "🔧 Verificando dependências Python..."
pip install -q flask flask-cors pandas openpyxl groq crewai python-dotenv

echo ""
echo "🔧 Verificando dependências Node.js..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências React..."
    npm install
fi
cd ..

echo ""
echo "🔍 Verificando configuração..."

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando exemplo..."
    cat > .env << EOF
# Configuração FinaCrew
GROQ_API_KEY=SUA_CHAVE_GROQ_AQUI
MODEL=llama3-8b-8192
REQUEST_DELAY=2
REQUEST_TIMEOUT=60
MAX_RETRIES=3
EOF
    echo "📝 Arquivo .env criado. Configure sua GROQ_API_KEY antes de usar."
fi

# Verificar diretórios
mkdir -p raw_data output temp_uploads

echo ""
echo "🚀 Iniciando serviços..."

# Função para cleanup ao sair
cleanup() {
    echo ""
    echo "🛑 Parando serviços..."
    kill_port 3000
    kill_port 5001
    echo "✅ Serviços parados."
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Iniciar API Flask em background
echo "🐍 Iniciando API Python (porta 5001)..."
cd api
PORT=5001 python3 app.py &
API_PID=$!
cd ..

# Aguardar API iniciar
echo "⏳ Aguardando API inicializar..."
sleep 5

# Verificar se API está rodando
if ! check_port 5001; then
    echo "❌ Erro ao iniciar API Python"
    exit 1
fi

echo "✅ API Python rodando na porta 5001"

# Iniciar React em background
echo "⚛️  Iniciando interface React (porta 3000)..."
cd frontend
npm start &
REACT_PID=$!
cd ..

# Aguardar React iniciar
echo "⏳ Aguardando React inicializar..."
sleep 10

# Verificar se React está rodando
if ! check_port 3000; then
    echo "❌ Erro ao iniciar React"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ React rodando na porta 3000"

echo ""
echo "🎉 FinaCrew iniciado com sucesso!"
echo "📍 URLs disponíveis:"
echo "   🌐 Interface Web: http://localhost:3000"
echo "   📡 API Backend:   http://localhost:5001"
echo "   📋 API Health:    http://localhost:5001/api/health"
echo ""
echo "💡 Comandos úteis:"
echo "   Ctrl+C - Parar todos os serviços"
echo "   ./stop_dev.sh - Parar serviços manualmente"
echo ""
echo "📖 Guia de uso:"
echo "   1. Acesse http://localhost:3000"
echo "   2. Faça upload dos 5 arquivos Excel obrigatórios"
echo "   3. Clique em 'Iniciar Processamento'"
echo "   4. Aguarde o processamento e baixe os resultados"
echo ""
echo "⏳ Serviços rodando... (Pressione Ctrl+C para parar)"

# Aguardar indefinidamente
while true; do
    if ! check_port 5001; then
        echo "❌ API Python parou inesperadamente"
        break
    fi
    if ! check_port 3000; then
        echo "❌ React parou inesperadamente"
        break
    fi
    sleep 5
done

cleanup