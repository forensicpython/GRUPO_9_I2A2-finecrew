# Multi-stage build para otimizar tamanho da imagem
FROM node:18-alpine AS frontend-build

# Configurar diretório de trabalho para frontend
WORKDIR /app/frontend

# Copiar package.json e package-lock.json
COPY frontend/package*.json ./

# Instalar dependências
RUN npm ci --only=production

# Copiar código fonte do frontend
COPY frontend/ ./

# Build do React para produção
RUN npm run build

# Stage 2: Python backend + frontend estático
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte do backend
COPY api/ ./api/
COPY src/ ./src/
COPY tools/ ./tools/
COPY *.py ./

# Copiar build do frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Criar diretórios necessários
RUN mkdir -p uploads temp_data

# Configurar variáveis de ambiente
ENV FLASK_APP=api/app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Expor porta
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "api.app:app"]