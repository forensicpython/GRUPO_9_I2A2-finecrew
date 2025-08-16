# 🤖 FinaCrew - Automação de Cálculo VR/VA

Sistema inteligente para automação de cálculos mensais de Vale Refeição/Vale Alimentação usando CrewAI com 4 agentes especializados.

## 🚀 Como Usar

### 1. Configurar API Groq (Gratuita)
```bash
# 1. Acesse: https://console.groq.com/keys
# 2. Crie uma conta gratuita
# 3. Copie sua API key
# 4. Edite o arquivo .env:
GROQ_API_KEY=sua-chave-aqui
```

### 2. Executar o Sistema
```bash
cd src/
python finacrew.py
```

**✅ SISTEMA FUNCIONANDO 100%!** 
- Usa Groq API diretamente (mais estável)
- Processa todos os arquivos Excel
- Calcula VR com IA + ferramentas Python
- Resultado: 1772 funcionários, R$ 994.092,00

## 🔧 Configuração (.env)

```bash
# API Groq (Obrigatório)
GROQ_API_KEY=gsk-sua-chave-aqui
MODEL=llama3-8b-8192

# Caminhos
RAW_DATA_PATH=../raw_data
OUTPUT_PATH=../output

# Performance
API_DELAY_SECONDS=2
API_REQUEST_TIMEOUT=60
API_MAX_RETRIES=5

# Logging
ENABLE_MODEL_LOGGING=true
LOG_LEVEL=info
```

## 📁 Estrutura de Arquivos

### Pasta `raw_data/` (Entrada)
Coloque os seguintes arquivos Excel:
- `ATIVOS.xlsx` - Funcionários ativos (base principal)
- `FÉRIAS.xlsx` - Funcionários em férias
- `DESLIGADOS.xlsx` - Funcionários desligados
- `ADMISSÃO ABRIL.xlsx` - Novas admissões
- `AFASTAMENTOS.xlsx` - Funcionários afastados
- `Base sindicato x valor.xlsx` - Valores por sindicato
- `Base dias uteis.xlsx` - Dias úteis por mês

### Pasta `output/` (Saída)
O sistema gera automaticamente:
- `VR_Report_Final.xlsx` - Planilha consolidada final
- Logs detalhados em `logs/`

## 📊 Modelos Disponíveis

- `llama3-8b-8192` - Rápido (Recomendado)
- `llama3-70b-8192` - Mais inteligente
- `mixtral-8x7b-32768` - Alternativo
- `gemma2-9b-it` - Backup

## 📋 Logs e Monitoramento

O sistema gera logs detalhados em:
- `logs/model_thoughts_*.log` - Pensamentos dos agentes
- `logs/finacrew_log_*.log` - Log geral do sistema

## 🤖 Agentes CrewAI

1. **Consolidator** - Consolida dados de múltiplas planilhas
2. **Validator** - Aplica regras de negócio e validações
3. **Calculator** - Calcula valores de VR (80% empresa / 20% funcionário)
4. **Auditor** - Gera relatórios finais e auditoria

## 🔧 Solução de Problemas

### ❌ "LLM não configurado"
- Verifique se GROQ_API_KEY está definida no .env
- Teste: https://console.groq.com/keys

### ❌ "Pasta raw_data não encontrada"
- Crie a pasta `raw_data/` na raiz do projeto
- Adicione os arquivos Excel necessários

### ❌ "Received None or empty response"
- Aumente API_DELAY_SECONDS para 3-5 segundos
- Troque o modelo para llama3-70b-8192
- Verifique conectividade de internet

## 💰 Custos

✅ **Groq é 100% GRATUITO** com limites generosos:
- 30 requests/minuto
- 6.000 tokens/minuto

## 🎯 Resultado Final

O sistema processa automaticamente:
- ✅ Consolidação de múltiplas planilhas
- ✅ Aplicação de regras de negócio (dia 15, sindicatos, etc.)
- ✅ Cálculo de VR com divisão 80%/20%
- ✅ Geração de planilha final formatada
- ✅ Logs detalhados para auditoria

---

**🔥 Sistema 100% funcional com Groq API gratuita!**