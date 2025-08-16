# FinaCrew v2.1 - Configuração Dinâmica da API Groq

Sistema automatizado de processamento de VR/VA com configuração personalizada da API Groq direto na interface.

## 🆕 Novidades da v2.1

### Configuração Dinâmica da API Groq
- **Configuração na Interface** - Insira sua chave API diretamente na tela
- **Seleção de Modelo** - Escolha entre 4 modelos disponíveis
- **Teste de Conexão** - Valide sua configuração antes de processar
- **Configurações Avançadas** - Ajuste timeout, delay e tentativas
- **Segurança** - Chave não é armazenada, apenas usada na sessão

### Interface Aprimorada
- **4 Etapas Claras**: Configuração → Upload → Processamento → Resultados
- **Validação em Tempo Real** - Teste sua API antes de usar
- **Interface Intuitiva** - Guias visuais para cada configuração
- **Salvamento de Preferências** - Configurações salvas localmente (exceto chave)

## 🚀 Como Usar a Nova Versão

### 1. Configuração Inicial
```bash
# Iniciar o sistema
./start_dev.sh

# Acessar: http://localhost:3000
```

### 2. Nova Etapa: Configuração da API
1. **Obter Chave Groq**:
   - Acesse: https://console.groq.com
   - Faça login ou crie conta gratuita
   - Gere uma nova API Key

2. **Configurar na Interface**:
   - Cole sua chave API
   - Escolha o modelo (recomendado: Llama 3 8B)
   - Teste a conexão
   - Salve e continue

3. **Configurações Avançadas** (opcional):
   - Delay entre requests: 1-10s
   - Timeout por request: 30-300s
   - Máximo de tentativas: 1-5

### 3. Fluxo Completo Atualizado
1. ⚙️ **Configuração** - Configure sua API Groq
2. 📤 **Upload** - Carregue os 5 arquivos Excel
3. ⚡ **Processamento** - Execute com sua configuração
4. 📊 **Resultados** - Baixe os arquivos gerados

## 🔧 Modelos Disponíveis

### Llama 3 8B (Recomendado)
- **ID**: `llama3-8b-8192`
- **Uso**: Rápido e eficiente para FinaCrew
- **Vantagem**: Melhor custo-benefício

### Llama 3 70B
- **ID**: `llama3-70b-8192`
- **Uso**: Análises mais complexas
- **Vantagem**: Maior precisão

### Mixtral 8x7B
- **ID**: `mixtral-8x7b-32768`
- **Uso**: Performance geral balanceada
- **Vantagem**: Boa versatilidade

### Gemma 7B
- **ID**: `gemma-7b-it`
- **Uso**: Processamento leve
- **Vantagem**: Mais rápido

## 🔒 Segurança e Privacidade

### Proteção da Chave API
- ✅ **Não armazenada** - Usada apenas durante a sessão
- ✅ **HTTPS obrigatório** - Comunicação criptografada
- ✅ **Headers seguros** - Transmissão protegida
- ✅ **Limpeza automática** - Removida ao reiniciar

### Configurações Salvas
- ✅ **Modelo preferido** - Salvo no navegador
- ✅ **Configurações avançadas** - Persistem entre sessões
- ❌ **Chave API** - Nunca armazenada localmente

## 📡 API Atualizada

### Novo Endpoint: Teste de Configuração
```bash
POST /api/test-groq-config
Content-Type: application/json

{
  "apiKey": "gsk_...",
  "model": "llama3-8b-8192",
  "requestDelay": 2,
  "requestTimeout": 60,
  "maxRetries": 3
}
```

**Resposta de Sucesso:**
```json
{
  "status": "success",
  "message": "Conexão com Groq estabelecida com sucesso!",
  "model_used": "llama3-8b-8192",
  "test_response": "OK"
}
```

### Headers de Configuração
Todos os endpoints agora aceitam o header `X-Groq-Config`:
```bash
X-Groq-Config: {"apiKey":"gsk_...","model":"llama3-8b-8192",...}
```

## 🔄 Migração da v2.0

### Se você já tem o FinaCrew v2.0:
1. **Atualizar arquivos** - Novos componentes adicionados
2. **Primeiro uso** - Configure sua API na nova tela
3. **Funcionamento** - Resto permanece igual

### Diferenças principais:
- **Antes**: Chave no arquivo `.env`
- **Agora**: Chave na interface web
- **Vantagem**: Múltiplos usuários, múltiplas chaves

## 🛠️ Desenvolvimento

### Estrutura Atualizada
```
FinaCrew/
├── frontend/src/components/
│   ├── ConfigurationStep.tsx    # 🆕 Configuração Groq
│   ├── FileUploader.tsx
│   ├── ProcessingDashboard.tsx
│   └── ResultsView.tsx
├── api/
│   └── app.py                   # 🆕 Endpoint teste Groq
└── scripts/
```

### Novos Recursos de Desenvolvimento
- **Configuração dinâmica** - Sem restart necessário
- **Teste isolado** - Valide API sem processamento
- **Debug melhorado** - Logs de configuração

## 📊 Comparação de Versões

| Recurso | v2.0 | v2.1 |
|---------|------|------|
| Interface Web | ✅ | ✅ |
| Upload Drag&Drop | ✅ | ✅ |
| Dashboard Tempo Real | ✅ | ✅ |
| **Configuração API** | .env | **Interface** |
| **Teste Conexão** | ❌ | **✅** |
| **Múltiplos Modelos** | ❌ | **✅** |
| **Config Avançadas** | ❌ | **✅** |
| **Multi-usuário** | ❌ | **✅** |

## ⚡ Performance e Otimizações

### Configurações Recomendadas

**Para Velocidade:**
```json
{
  "model": "llama3-8b-8192",
  "requestDelay": 1,
  "requestTimeout": 30,
  "maxRetries": 2
}
```

**Para Precisão:**
```json
{
  "model": "llama3-70b-8192", 
  "requestDelay": 3,
  "requestTimeout": 90,
  "maxRetries": 3
}
```

**Para Economia:**
```json
{
  "model": "gemma-7b-it",
  "requestDelay": 2,
  "requestTimeout": 45,
  "maxRetries": 1
}
```

## 🚨 Troubleshooting

### Problemas Comuns

**❌ "Erro na conexão com Groq"**
- Verificar chave API válida
- Testar conexão na tela de configuração
- Verificar internet estável

**❌ "Modelo não disponível"**
- Verificar limite da conta Groq
- Tentar modelo diferente
- Verificar status da API Groq

**❌ "Timeout na requisição"**
- Aumentar timeout nas configurações
- Verificar estabilidade da rede
- Reduzir requestDelay

### Logs de Debug
```bash
# Logs da API
tail -f api/logs/app.log

# Logs do navegador
F12 → Console → Filtrar "FinaCrew"
```

## 🎯 Próximas Versões

### v2.2 - Planejada
- [ ] **Histórico de Configurações** - Salvar múltiplas configs
- [ ] **Templates de Configuração** - Configs pré-definidas
- [ ] **Monitoramento de Uso** - Tracking de tokens/custo
- [ ] **Configuração por Projeto** - Diferentes configs por tipo

### v2.3 - Futuro
- [ ] **Múltiplas APIs** - Suporte OpenAI, Anthropic
- [ ] **Configuração de Time** - Compartilhar configs
- [ ] **Auditoria Completa** - Log de todas as configurações
- [ ] **Dashboard Admin** - Gerenciamento centralizado

## 🎉 Conclusão

**FinaCrew v2.1** traz flexibilidade total para configuração da API Groq:

✅ **Sem arquivo .env** - Configure direto na interface  
✅ **Teste antes de usar** - Valide sua configuração  
✅ **Múltiplos modelos** - Escolha o melhor para seu caso  
✅ **Configuração avançada** - Controle total do comportamento  
✅ **Multi-usuário** - Cada um com sua chave  
✅ **Segurança máxima** - Chave nunca armazenada  

### 🚀 Comece agora:
```bash
./start_dev.sh
# Acesse: http://localhost:3000
# Configure sua API Groq e processe!
```

---

**FinaCrew v2.1** - Configuração inteligente, processamento profissional! 🎯