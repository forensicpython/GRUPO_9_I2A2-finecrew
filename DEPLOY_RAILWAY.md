# 🚀 Deploy FinaCrew no Railway

## ✅ **PASSO A PASSO COMPLETO**

### **1. Criar Conta no Railway**
1. Acesse: https://railway.app
2. Clique em "Login" → "GitHub"
3. Faça login com sua conta GitHub
4. Aceite as permissões

### **2. Subir Código para GitHub**
```bash
# 1. Inicializar repositório Git (se ainda não fez)
cd /caminho/para/FinaCrew
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Fazer primeiro commit
git commit -m "🚀 FinaCrew v2.1 - Deploy Railway

✅ Interface React com design profissional
✅ Backend Flask otimizado
✅ 4 modelos de IA configurados
✅ Sistema completo de processamento VR/VA

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Criar repositório no GitHub
# - Vá em github.com
# - Clique em "New repository"
# - Nome: "finacrew-hanotas"
# - Público ou Privado (sua escolha)
# - NÃO marque "Initialize with README"
# - Clique "Create repository"

# 5. Conectar com GitHub
git remote add origin https://github.com/SEU_USUARIO/finacrew-hanotas.git
git branch -M main
git push -u origin main
```

### **3. Deploy no Railway**
1. **No Railway Dashboard:**
   - Clique "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório "finacrew-hanotas"
   - Clique "Deploy Now"

2. **Configurar Variáveis de Ambiente:**
   ```
   FLASK_ENV=production
   PORT=8080
   ```

3. **Railway vai detectar automaticamente:**
   - ✅ Dockerfile (configuração completa)
   - ✅ requirements.txt (dependências Python)
   - ✅ Build do React já está pronto

### **4. Configurar Domínio Customizado**
1. **No Railway:**
   - Vá em seu projeto
   - Clique na aba "Settings"
   - Seção "Domains"
   - Clique "Custom Domain"
   - Digite: `hanotas.com.br`

2. **No seu provedor DNS (onde registrou hanotas.com.br):**
   ```
   Tipo: CNAME
   Nome: @ (ou deixe vazio)
   Valor: [URL_FORNECIDA_PELO_RAILWAY]
   
   Tipo: CNAME  
   Nome: www
   Valor: [URL_FORNECIDA_PELO_RAILWAY]
   ```

### **5. URLs do Projeto**
- **Temporária Railway:** `https://finacrew-production-XXXX.up.railway.app`
- **Domínio Customizado:** `https://hanotas.com.br`

---

## 🔧 **Arquivos Criados para Deploy**

### ✅ **Dockerfile**
- Build multi-stage otimizado
- React + Flask em uma imagem
- Gunicorn para produção

### ✅ **railway.json**
- Configuração específica Railway
- Nixpacks builder
- Política de restart

### ✅ **requirements.txt**
- Todas dependências Python
- Versões específicas para estabilidade

### ✅ **start.sh**
- Script de inicialização
- Configuração de diretórios
- Gunicorn com workers

### ✅ **api/app.py atualizado**
- Servir React app estático
- Configuração de porta dinâmica
- Modo produção

---

## 💰 **Custos**
- **Railway Hobby Plan:** $5 USD/mês (~R$ 30/mês)
- **Recursos inclusos:**
  - 512MB RAM
  - 1GB storage
  - Builds ilimitados
  - Domínio customizado
  - SSL automático

---

## 🛠️ **Troubleshooting**

### **Build falha:**
```bash
# Verificar se build React existe
ls frontend/build

# Se não existir, fazer build local:
cd frontend && npm run build
```

### **Erro 404 nas rotas:**
- ✅ Arquivo .htaccess não necessário
- ✅ Flask configurado para servir React
- ✅ SPA routing configurado

### **API não funciona:**
- Verificar variáveis de ambiente
- Verificar logs no Railway Dashboard
- Testar endpoint: `https://SEU_APP.railway.app/api/health`

---

## 🎉 **Resultado Final**

Após o deploy, você terá:
- ✅ **hanotas.com.br** funcionando
- ✅ SSL automático (HTTPS)
- ✅ Interface React moderna
- ✅ API Flask robusta
- ✅ Deploy automático via GitHub
- ✅ Logs em tempo real
- ✅ Escalabilidade automática

**O FinaCrew estará 100% online e profissional!** 🚀