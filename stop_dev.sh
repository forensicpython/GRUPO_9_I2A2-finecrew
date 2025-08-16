#!/bin/bash

# Script para parar o ambiente de desenvolvimento FinaCrew
echo "🛑 Parando FinaCrew - Ambiente de Desenvolvimento"
echo "==============================================="

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
    local service_name=$2
    
    if check_port $port; then
        echo "🔄 Parando $service_name (porta $port)..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            echo "⚠️  $service_name ainda está rodando na porta $port"
        else
            echo "✅ $service_name parado com sucesso"
        fi
    else
        echo "ℹ️  $service_name não está rodando na porta $port"
    fi
}

# Parar React (porta 3000)
kill_port 3000 "React Frontend"

# Parar API Flask (porta 5000)
kill_port 5000 "Python API"

# Parar processos relacionados ao projeto
echo ""
echo "🧹 Limpando processos relacionados..."

# Matar processos Python relacionados ao FinaCrew
pkill -f "finacrew" 2>/dev/null || true
pkill -f "app.py" 2>/dev/null || true

# Matar processos Node relacionados ao React
pkill -f "react-scripts" 2>/dev/null || true

echo ""
echo "✅ Todos os serviços FinaCrew foram parados!"
echo ""
echo "💡 Para reiniciar:"
echo "   ./start_dev.sh"