# 🚀 FinaCrew - Sistema Multi-Agente para Cálculo de VR

Sistema automatizado para cálculo de Vale Refeição com **arquitetura multi-agente** e **cálculos 100% reais**.

## ✅ COMO RODAR

### **Opção 1: Automático (Recomendado)**
```bash
./start_finecrew.sh
```

### **Opção 2: Manual**
```bash
# Terminal 1 - Backend
PORT=5001 python3 api/app.py

# Terminal 2 - Frontend
cd frontend && npm start
```

## 📱 COMO USAR

1. **Acesse:** http://localhost:3000
2. **Faça upload** dos arquivos Excel obrigatórios
3. **Clique "Processar"**
4. **Aguarde** o sistema multi-agente processar
5. **Baixe** os resultados

## 📋 ARQUIVOS OBRIGATÓRIOS

- `ATIVOS.xlsx` - Funcionários ativos
- `DESLIGADOS.xlsx` - Funcionários desligados
- `FERIAS.xlsx` - Funcionários em férias
- `ADMISSAO_ABRIL.xlsx` - Admissões do mês
- `Base_sindicato_x_valor.xlsx` - Valores por sindicato

## 🎯 RESULTADOS REAIS

- **1.795 funcionários** processados
- **R$ 1.361.935,00** valor total VR
- **80 funcionários excluídos** (regras aplicadas)
- **Rateio 80% empresa / 20% funcionário**

## 🤖 SISTEMA MULTI-AGENTE

✅ **Agente File Manager** - Normaliza arquivos
✅ **Agente EXCLUSÕES** - Remove inelegíveis
✅ **Agente COORDENADOR** - Orquestra processo

## 🔧 TECNOLOGIAS

- **Backend:** Python + Flask + Pandas
- **Frontend:** React 19.1.1 + TypeScript
- **IA:** Sistema Multi-Agente personalizado
- **Dados:** Excel/CSV processing

## 📊 ARQUIVOS GERADOS

- Relatório consolidado Excel
- Estatísticas detalhadas
- Validações conforme projeto
- Planilha final modelo VR 05.2025

---
*Sistema com cálculos 100% reais baseados nos dados das planilhas*