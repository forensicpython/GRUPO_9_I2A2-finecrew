# FinaCrew v2.0 - Interface Web

Sistema automatizado de processamento de VR/VA com interface web moderna.

## 🚀 Novidades da v2.0

### Interface Web Completa
- **React + TypeScript** - Interface moderna e responsiva
- **Material-UI** - Design profissional e consistente
- **Upload Drag & Drop** - Carregamento intuitivo de arquivos
- **Dashboard em Tempo Real** - Acompanhamento do processamento
- **Visualizações Gráficas** - Charts e estatísticas interativas

### API REST
- **Flask Backend** - API robusta para comunicação
- **Endpoints RESTful** - Integração padronizada
- **CORS Habilitado** - Suporte completo para SPA
- **Error Handling** - Tratamento de erros abrangente

### Funcionalidades Principais
- ✅ Upload múltiplo de arquivos Excel
- ✅ Validação automática de arquivos obrigatórios
- ✅ Processamento em tempo real com logs
- ✅ Dashboard com estatísticas visuais
- ✅ Download direto dos resultados
- ✅ Interface step-by-step intuitiva
- ✅ Gráficos de distribuição e evolução
- ✅ Sistema de notificações

## 📋 Pré-requisitos

### Software Necessário
- **Python 3.8+** com pip
- **Node.js 16+** com npm
- **Chave Groq API** configurada

### Dependências Python
```bash
pip install flask flask-cors pandas openpyxl groq crewai python-dotenv
```

### Dependências Node.js
```bash
cd frontend
npm install
```

## 🏃‍♂️ Início Rápido

### 1. Configuração Inicial
```bash
# Clone/baixe o projeto
cd FinaCrew

# Configure a chave Groq no arquivo .env
echo "GROQ_API_KEY=sua_chave_aqui" > .env
```

### 2. Iniciar Ambiente de Desenvolvimento
```bash
# Opção 1: Script automático (recomendado)
./start_dev.sh

# Opção 2: Manual
# Terminal 1 - API Python
cd api && python3 app.py

# Terminal 2 - Interface React
cd frontend && npm start
```

### 3. Acessar a Aplicação
- **Interface Web**: http://localhost:3000
- **API Backend**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

### 4. Parar Serviços
```bash
# Opção 1: Ctrl+C no terminal do start_dev.sh
# Opção 2: Script de parada
./stop_dev.sh
```

## 📁 Estrutura do Projeto

```
FinaCrew/
├── frontend/                 # Interface React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── FileUploader.tsx
│   │   │   ├── ProcessingDashboard.tsx
│   │   │   └── ResultsView.tsx
│   │   ├── App.tsx          # Componente principal
│   │   └── index.tsx        # Entry point
│   ├── package.json
│   └── public/
├── api/                      # API Flask
│   └── app.py               # Servidor Flask
├── src/                      # Backend Python original
│   └── finacrew.py          # Lógica de processamento
├── tools/                    # Ferramentas de processamento
├── raw_data/                 # Arquivos Excel de entrada
├── output/                   # Arquivos gerados
├── start_dev.sh             # Script de inicialização
├── stop_dev.sh              # Script de parada
└── README_WEB.md            # Esta documentação
```

## 🎯 Como Usar

### Passo 1: Upload de Arquivos
1. Acesse http://localhost:3000
2. Arraste os arquivos Excel para a área de upload ou clique para selecionar
3. Aguarde todos os 5 arquivos obrigatórios serem carregados:
   - `ATIVOS.xlsx`
   - `FÉRIAS.xlsx`
   - `DESLIGADOS.xlsx`
   - `ADMISSÃO ABRIL.xlsx`
   - `Base sindicato x valor.xlsx`

### Passo 2: Processamento
1. Clique em "Iniciar Processamento"
2. Acompanhe o progresso em tempo real:
   - Upload dos arquivos
   - Consolidação das bases
   - Validação de qualidade
   - Cálculo automatizado
   - Geração da planilha
3. Visualize os logs detalhados

### Passo 3: Resultados
1. Visualize as estatísticas do processamento
2. Analise os gráficos de distribuição
3. Faça download dos arquivos gerados:
   - `base_consolidada.xlsx`
   - `calculo_automatizado_beneficios.xlsx`
   - `VR MENSAL 05.2025 vfinal.xlsx`

## 📊 Funcionalidades da Interface

### Dashboard Principal
- **Stepper Visual** - Progresso step-by-step
- **Cards de Estatísticas** - Métricas em tempo real
- **Progress Bars** - Indicadores visuais de progresso
- **Sistema de Logs** - Terminal em tempo real

### Upload de Arquivos
- **Drag & Drop** - Interface intuitiva
- **Validação Automática** - Verificação de arquivos obrigatórios
- **Preview de Arquivos** - Lista com informações detalhadas
- **Progress Indicator** - Barra de progresso do upload

### Visualização de Resultados
- **Gráfico de Pizza** - Distribuição empresa/funcionário
- **Gráfico de Barras** - Evolução mensal
- **Cards de KPIs** - Métricas principais
- **Lista de Downloads** - Arquivos gerados

## 🔧 API Endpoints

### GET /api/health
Verificar status da API
```json
{
  "status": "healthy",
  "message": "FinaCrew API está funcionando!",
  "version": "2.0"
}
```

### POST /api/upload
Upload de arquivos Excel
```bash
curl -X POST -F "files=@ATIVOS.xlsx" http://localhost:5000/api/upload
```

### POST /api/process
Processar arquivos carregados
```bash
curl -X POST http://localhost:5000/api/process
```

### GET /api/download/{filename}
Download de arquivo gerado
```bash
curl -O http://localhost:5000/api/download/VR_MENSAL_05.2025_vfinal.xlsx
```

### GET /api/files
Listar arquivos gerados
```bash
curl http://localhost:5000/api/files
```

### GET /api/status
Status do sistema
```bash
curl http://localhost:5000/api/status
```

## 🐛 Troubleshooting

### Problema: Porta em uso
```bash
# Verificar portas em uso
lsof -i :3000
lsof -i :5000

# Matar processos
./stop_dev.sh
```

### Problema: Dependências não instaladas
```bash
# Python
pip install -r requirements.txt

# Node.js
cd frontend && npm install
```

### Problema: GROQ_API_KEY não configurada
```bash
# Editar arquivo .env
echo "GROQ_API_KEY=sua_chave_real_aqui" > .env
```

### Problema: Arquivos não encontrados
```bash
# Verificar estrutura
ls -la raw_data/
ls -la output/
```

## 🔄 Desenvolvimento

### Estrutura de Componentes React

#### FileUploader.tsx
- Upload drag & drop
- Validação de arquivos
- Progress tracking
- Preview de arquivos

#### ProcessingDashboard.tsx
- Execução do processamento
- Logs em tempo real
- Indicadores visuais
- Conexão com API

#### ResultsView.tsx
- Visualização de resultados
- Gráficos interativos
- Download de arquivos
- Estatísticas detalhadas

### Fluxo de Dados
1. **Frontend** → Upload de arquivos → **API**
2. **API** → Salva arquivos → **Backend Python**
3. **Backend** → Processa dados → **Gera resultados**
4. **API** → Retorna resultados → **Frontend**
5. **Frontend** → Exibe resultados → **Download**

## 📈 Próximas Versões

### v2.1 - Melhorias Planejadas
- [ ] Histórico de processamentos
- [ ] Configuração de regras via interface
- [ ] Notificações por email
- [ ] Exportação para PDF
- [ ] Temas customizáveis

### v2.2 - Integrações
- [ ] API de terceiros
- [ ] Banco de dados
- [ ] Autenticação de usuários
- [ ] Logs de auditoria
- [ ] Backup automático

## 📞 Suporte

Para suporte e dúvidas:
1. Verifique esta documentação
2. Execute `./start_dev.sh` para diagnósticos
3. Verifique os logs da API e do React
4. Consulte a documentação original do FinaCrew

---

**FinaCrew v2.0** - Sistema profissional de processamento VR/VA com interface web moderna e intuitiva.