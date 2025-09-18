# FinaCrew - Sistema VR/VA Automatizado

Sistema multi-agente focado nos objetivos essenciais do PDF: automatização do processo de compra mensal de VR/VA.

## Estrutura Essencial

```
FinaCrew/
├── finacrew.py              # Core principal CrewAI com decoradores
├── config/                  # Configurações YAML dos agentes e tasks
├── tools/                   # Ferramentas especializadas
├── api/app.py              # API Flask simplificada
├── start_finecrew.sh       # Script de inicialização
├── requirements.txt        # Dependências essenciais
├── .env                    # Configurações de ambiente
└── descrição_do_projeto.pdf # Especificação original

```

## Objetivos Implementados

1. ✅ **Consolidação de bases**: 5 planilhas em uma única base
2. ✅ **Aplicação de exclusões**: Diretores, estagiários, aprendizes, afastamentos, exterior
3. ✅ **Cálculo de dias úteis**: Por sindicato/região considerando feriados
4. ✅ **Regra do dia 15**: Funcionários desligados até dia 15
5. ✅ **Divisão 80/20**: Empresa/Funcionário conforme especificação
6. ✅ **Geração de planilha**: "VR MENSAL 05.2025 vfinal.xlsx"

## Uso

```bash
# Executar sistema completo
./start_finecrew.sh

# Ou apenas o core
python3 finacrew.py

# Ou via API
python3 api/app.py
```

## Dependências

Apenas o essencial para os objetivos:
- CrewAI (sistema multi-agente)
- Groq (LLM provider)
- Pandas/OpenPyXL (processamento de planilhas)
- Flask (API mínima)

Todos os arquivos desnecessários foram removidos para manter foco nos objetivos do PDF.