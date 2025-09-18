# Funcionamento do Sistema FinaCrew - Arquitetura Multi-Agente

## 📋 Visão Geral

O **FinaCrew** é um sistema multi-agente baseado no framework **CrewAI** que automatiza o processamento de Vale Refeição/Vale Alimentação (VR/VA) através de inteligência artificial. O sistema substitui processamento manual por uma solução inteligente que aplica regras de negócio complexas de forma autônoma.

## 🎯 Objetivo do Sistema

- **Automatizar** o cálculo de VR/VA para funcionários
- **Aplicar regras empresariais** conforme especificações do PDF
- **Gerar planilhas** finais com validações completas
- **Fornecer auditoria** completa do processamento
- **Garantir conformidade** com critérios de elegibilidade

## 🤖 Arquitetura dos Agentes

O sistema possui **3 agentes principais** que trabalham de forma sequencial e colaborativa:

### **1. File Manager Agent (Gerenciador de Arquivos)**

**📁 Especialista em Normalização e Carregamento de Dados**

- **Função Principal**: Descobrir, validar e normalizar arquivos Excel
- **Responsabilidades**:
  - Localizar arquivos nas pastas `raw_data` e `temp_uploads`
  - Validar integridade dos dados de entrada
  - Normalizar nomes de colunas e estruturas
  - Carregar as **5 bases obrigatórias**:
    - Base de Funcionários Ativos
    - Base de Férias
    - Base de Desligados
    - Base de Admitidos
    - Base Sindicato x Valor
  - Garantir qualidade dos dados antes do processamento

- **Ferramentas Utilizadas**:
  - `file_discovery_tool`: Descoberta automática de arquivos
  - `spreadsheet_analyzer_tool`: Análise de estrutura das planilhas

- **Localização**: `config/agents.yaml` → `file_manager_agent`

### **2. Exclusions Agent (Agente de Exclusões)**

**🚫 Especialista em Regras de Negócio e Exclusões**

- **Função Principal**: Aplicar critérios de elegibilidade e exclusões
- **Responsabilidades**:
  - Aplicar **exclusões obrigatórias**:
    - Diretores
    - Estagiários
    - Aprendizes
    - Funcionários afastados
    - Funcionários no exterior
  - Implementar **regra de desligamento**:
    - Até dia 15: não paga VR/VA
    - Após dia 15: valor proporcional
  - Validar elegibilidade conforme critérios empresariais
  - Gerar **relatório de auditoria** dos funcionários excluídos
  - Aplicar regras específicas por sindicato

- **Ferramentas Utilizadas**:
  - `working_days_calculator_tool`: Cálculo de dias úteis

- **Localização**: `config/agents.yaml` → `exclusions_agent`

### **3. Coordinator Agent (Agente Coordenador)**

**🎯 Coordenador Geral do Processamento VR/VA**

- **Função Principal**: Orquestrar o fluxo completo e gerar saídas finais
- **Responsabilidades**:
  - Coordenar todo o fluxo de processamento
  - Calcular valores finais com divisão:
    - **80% empresa**
    - **20% funcionário**
  - Gerar **planilha consolidada** `VR MENSAL 05.2025.xlsx`
  - Coordenar criação de todos os arquivos de saída
  - Validar resultados finais
  - Gerar relatórios de auditoria

- **Ferramentas Utilizadas**:
  - `model_excel_generator_tool`: Geração de planilhas Excel

- **Localização**: `config/agents.yaml` → `coordinator_agent`

## 📋 Fluxo de Tarefas Sequenciais

O sistema executa **5 tarefas principais** em sequência rigorosa:

### **Task 1: Descoberta de Arquivos** 🔍
- **Agente Responsável**: File Manager Agent
- **Objetivo**: Localizar e catalogar todos os arquivos Excel necessários
- **Processo**:
  - Scan das pastas `raw_data` e `temp_uploads`
  - Validação de formatos (.xlsx, .xls)
  - Verificação de integridade dos arquivos
- **Output**: Lista completa dos arquivos encontrados e validados

### **Task 2: Análise de Estrutura** 📊
- **Agente Responsável**: File Manager Agent
- **Objetivo**: Analisar estrutura e conteúdo de cada planilha
- **Processo**:
  - Mapeamento de colunas por arquivo
  - Identificação de tipos de dados
  - Validação de estruturas esperadas
- **Output**: Mapeamento detalhado das colunas e dados de cada base

### **Task 3: Consolidação da Base** 🔗
- **Agente Responsável**: File Manager Agent
- **Objetivo**: Unificar as 5 fontes de dados em uma base consolidada
- **Processo**:
  - Normalização de estruturas de dados
  - Merge inteligente das bases
  - Resolução de conflitos de dados
  - Criação de chaves únicas
- **Output**: Base de dados única e normalizada para processamento

### **Task 4: Aplicação de Exclusões** ❌
- **Agente Responsável**: Exclusions Agent
- **Objetivo**: Aplicar todas as regras de exclusão e eligibilidade
- **Processo**:
  - Identificação de funcionários por categoria
  - Aplicação de regras de desligamento
  - Validação de critérios de elegibilidade
  - Cálculo de dias úteis por funcionário
- **Output**:
  - Lista final de funcionários elegíveis
  - Relatório detalhado de exclusões para auditoria

### **Task 5: Geração dos Arquivos Finais** 📄
- **Agente Responsável**: Coordinator Agent
- **Objetivo**: Calcular valores e gerar planilhas finais
- **Processo**:
  - Cálculo de valores VR/VA por funcionário
  - Aplicação da divisão 80% empresa / 20% funcionário
  - Geração de planilhas formatadas
  - Validação de totais e consistência
- **Output**:
  - `VR MENSAL 05.2025.xlsx` (planilha principal)
  - `FUNCIONARIOS_EXCLUIDOS_AUDITORIA.xlsx` (relatório de exclusões)

## 🔧 Sistema de Análise Inteligente

### **Agente Analisador de Resultados**

Substituímos a extração por regex por um **agente analisador especializado**:

**Arquivo**: `tools/results_analyzer_agent_tool.py`

**Características**:
- **LLM**: Groq (Llama 3.3 70B Versatile)
- **Função**: Extrair dados estruturados do processamento
- **Validações**: Aplicar regras de negócio do PDF empresarial
- **Output**: JSON estruturado com todos os dados necessários

**Validações Realizadas**:
- ✅ Regras de sindicato aplicadas
- ✅ Exclusões aplicadas corretamente
- ✅ Regra de desligamento implementada
- ✅ Divisão de custos 80%/20% correta

**Exemplo de Output**:
```json
{
  "funcionarios_elegiveis": 1719,
  "valor_total_vr": 1385943.75,
  "valor_empresa": 1108755.00,
  "valor_funcionario": 277188.75,
  "arquivos_gerados": ["VR MENSAL 05.2025.xlsx", "FUNCIONARIOS_EXCLUIDOS_AUDITORIA.xlsx"],
  "tempo_processamento": "Real-time",
  "validacoes": {
    "regras_sindicato_aplicadas": true,
    "exclusoes_aplicadas": true,
    "regra_desligamento_aplicada": true,
    "divisao_custo_correta": true
  },
  "metodo_extracao": "agente_analisador"
}
```

## 🌐 Integração Sistema Completo

### **Backend (Flask API)** 🐍

**Arquivo Principal**: `api/app.py`

**Endpoints Principais**:
- `/api/process`: Orquestra todo o processamento VR/VA
- `/api/upload`: Upload de arquivos Excel
- `/api/download/<filename>`: Download de resultados
- `/api/test-groq`: Teste de conectividade com IA

**Fluxo de Processamento**:
1. Recebe arquivos via upload
2. Configura credenciais Groq via headers
3. Inicia captura de logs dos agentes
4. Processa dados reais via `real_data_processor_tool`
5. Analisa resultados via `results_analyzer_agent_tool`
6. Retorna dados estruturados + downloads disponíveis

### **Frontend (React + Material-UI)** ⚛️

**Características**:
- Interface moderna e responsiva
- Upload drag-and-drop de arquivos
- Configuração de credenciais Groq API
- Teste de conectividade em tempo real
- Download automático dos resultados
- Monitoramento de progresso

**Páginas Principais**:
- **ConfigurationPage**: Configuração de credenciais
- **ProcessingPage**: Upload e processamento
- **ResultsPage**: Visualização e download

### **Sistema de Logging e Auditoria** 📝

**Arquivo**: `tools/agent_logger_tool.py`

**Características**:
- **Captura completa** de conversas dos agentes
- **Logs estruturados** em formato JSON e texto
- **Timestamps** precisos para auditoria
- **Rastreamento** de todas as decisões dos agentes
- **Download** dos logs para transparência

**Estrutura dos Logs**:
```json
{
  "session_info": {
    "start_time": "2025-01-XX",
    "duration_seconds": 120,
    "total_logs": 45
  },
  "logs": [
    {
      "timestamp": "2025-01-XX 10:30:00",
      "agent": "File Manager Agent",
      "level": "INFO",
      "message": "Arquivos descobertos: 5 bases encontradas"
    }
  ],
  "summary": {
    "agents_involved": ["File Manager", "Exclusions", "Coordinator"],
    "log_levels": ["INFO", "LOG", "RESULT"]
  }
}
```

## ⚡ Vantagens da Arquitetura Multi-Agente

### **1. Especialização** 🎯
- Cada agente é expert em sua área específica
- Conhecimento profundo das regras de negócio
- Otimização de performance por especialização

### **2. Flexibilidade** 🔄
- Fácil modificação de regras por agente
- Adição de novos agentes sem impacto
- Configuração via YAML para mudanças rápidas

### **3. Transparência** 🔍
- Logs detalhados de todas as decisões
- Rastreabilidade completa do processamento
- Auditoria de cada etapa do fluxo

### **4. Escalabilidade** 📈
- Possibilidade de adicionar novos agentes
- Paralelização de tarefas independentes
- Arquitetura preparada para crescimento

### **5. Inteligência** 🧠
- Uso de LLM para análise contextual
- Substituição de regex fixo por compreensão semântica
- Adaptação automática a variações nos dados

## 🛠️ Tecnologias Utilizadas

### **Framework de Agentes**
- **CrewAI**: Orquestração de agentes
- **LangChain**: Base para ferramentas de IA

### **Inteligência Artificial**
- **Groq API**: Processamento de linguagem natural
- **Llama 3.3 70B**: Modelo de linguagem principal

### **Backend**
- **Flask**: API REST
- **Python 3.x**: Linguagem principal
- **Pandas**: Manipulação de dados
- **OpenPyXL**: Processamento de Excel

### **Frontend**
- **React**: Interface de usuário
- **Material-UI**: Componentes visuais
- **TypeScript**: Tipagem estática

### **Configuração**
- **YAML**: Configuração de agentes e tarefas
- **Environment Variables**: Credenciais e configurações

## 📁 Estrutura de Arquivos

```
FinaCrew/
├── api/
│   └── app.py                 # API Flask principal
├── config/
│   ├── agents.yaml           # Configuração dos agentes
│   └── tasks.yaml            # Definição das tarefas
├── tools/
│   ├── agent_logger_tool.py           # Sistema de logging
│   ├── results_analyzer_agent_tool.py # Analisador inteligente
│   ├── real_data_processor_tool.py    # Processador de dados
│   └── [outras ferramentas]
├── frontend/
│   └── src/
│       ├── pages/            # Páginas React
│       └── types/            # Definições TypeScript
├── finacrew.py               # Orquestrador principal CrewAI
└── start_finecrew.sh         # Script de inicialização
```

## 🎯 Conclusão

O **FinaCrew** representa uma evolução significativa no processamento automatizado de VR/VA, combinando:

- **Inteligência Artificial** para compreensão semântica
- **Arquitetura Multi-Agente** para especialização
- **Interface Moderna** para usabilidade
- **Auditoria Completa** para conformidade
- **Flexibilidade** para adaptações futuras

O sistema garante **conformidade total** com as especificações empresariais através da colaboração inteligente entre agentes especializados, cada um executando sua função no fluxo de processamento VR/VA com precisão e transparência.