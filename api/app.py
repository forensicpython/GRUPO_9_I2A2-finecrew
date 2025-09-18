#!/usr/bin/env python3
"""
API Flask para FinaCrew - Interface entre React e Python
"""

import os
import sys
import tempfile
import shutil
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import subprocess

# Configurar logging para reduzir verbose
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('werkzeug').disabled = True

# Configurar o path para importar o FinaCrew
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar nova estrutura FinaCrew com decoradores
from finacrew import process_vr_calculation

# Importar ferramenta de dados reais
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from real_data_processor_tool import real_data_processor_tool
from results_analyzer_agent_tool import results_analyzer_agent_tool
from agent_logger_tool import agent_logger_tool

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)  # Permitir requisições do React

# Configurações
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Criar diretório de upload se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def serve_frontend():
    """Servir a aplicação React"""
    try:
        return app.send_static_file('index.html')
    except:
        # Se não há build do React, retornar mensagem simples
        return jsonify({"message": "FinaCrew API está funcionando! Frontend não encontrado."})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "FinaCrew API"})


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Endpoint para upload de arquivos Excel"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "Nenhum arquivo foi enviado"}), 400

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400

        uploaded_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append({
                    "name": filename,
                    "size": os.path.getsize(filepath),
                    "path": filepath
                })
            else:
                return jsonify({"error": f"Arquivo não permitido: {file.filename}"}), 400

        return jsonify({
            "message": f"{len(uploaded_files)} arquivo(s) carregado(s) com sucesso",
            "files": uploaded_files
        })

    except Exception as e:
        return jsonify({"error": f"Erro no upload: {str(e)}"}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """Listar arquivos carregados"""
    try:
        files = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.isfile(filepath):
                    files.append({
                        "name": filename,
                        "size": os.path.getsize(filepath),
                        "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    })

        return jsonify({"files": files})

    except Exception as e:
        return jsonify({"error": f"Erro ao listar arquivos: {str(e)}"}), 500


@app.route('/api/test-groq-config', methods=['POST'])
def test_groq_config():
    """Testar configuração do Groq"""
    try:
        data = request.get_json()
        api_key = data.get('apiKey')
        model = data.get('model', 'llama-3.3-70b-versatile')

        if not api_key:
            return jsonify({"error": "API key é obrigatória"}), 400

        # Teste simples com a API do Groq
        import requests

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        test_payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 10
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=test_payload,
            timeout=30
        )

        if response.status_code == 200:
            return jsonify({
                "success": True,
                "message": "Conexão com Groq estabelecida com sucesso",
                "model_used": model
            })
        else:
            error_data = response.json() if response.content else {}
            return jsonify({
                "error": error_data.get("error", {}).get("message", f"Erro {response.status_code}")
            }), response.status_code

    except Exception as e:
        return jsonify({"error": f"Erro ao testar Groq: {str(e)}"}), 500


@app.route('/api/process', methods=['POST'])
def process_vr():
    """
    Endpoint principal para processamento VR/VA
    Usa exclusivamente o agente analisador para extrair dados
    """
    try:
        print("🚀 Iniciando processamento FinaCrew com Agente Analisador...")

        # Iniciar captura de logs dos agentes
        session_id = agent_logger_tool.func("start", "", "API_PROCESS")

        # Obter configuração do Groq dos headers
        groq_config_header = request.headers.get('X-Groq-Config')
        if groq_config_header:
            groq_config = json.loads(groq_config_header)
            os.environ["GROQ_API_KEY"] = groq_config.get('apiKey', os.getenv('GROQ_API_KEY'))
            os.environ["MODEL"] = groq_config.get('model', os.getenv('MODEL', 'llama-3.3-70b-versatile'))
            agent_logger_tool.func("log", f"Configuração Groq aplicada: {groq_config.get('model', 'default')}", "CONFIG")

        # Usar dados REAIS
        agent_logger_tool.func("log", "Iniciando processamento de dados reais", "DATA_PROCESSOR")
        real_data_result = real_data_processor_tool.func("temp_uploads")
        agent_logger_tool.func("log", f"Dados processados: {len(str(real_data_result))} caracteres", "DATA_PROCESSOR")

        # Usar agente analisador para extrair dados com validações empresariais
        print("🧠 Analisando resultados com agente especializado...")
        agent_logger_tool.func("log", "Iniciando análise com agente especializado", "ANALYZER_AGENT")
        agent_result = results_analyzer_agent_tool.func(real_data_result)
        agent_logger_tool.func("crew_result", agent_result, "ANALYZER_AGENT")

        # Parse do resultado do agente
        agent_data = json.loads(agent_result)
        agent_logger_tool.func("log", f"Resultado parseado: {agent_data.get('funcionarios_elegiveis', 0)} funcionários", "PARSER")

        # Salvar logs e obter caminho do arquivo
        log_file_path = agent_logger_tool.func("save", "", "API_PROCESS")
        log_filename = os.path.basename(log_file_path) if log_file_path else "log_indisponivel.txt"

        print("✅ Processamento concluído com Agente Analisador!")
        return jsonify({
            "status": "success",
            "message": "Processamento VR/VA concluído com agente analisador",
            "funcionarios_elegiveis": agent_data.get("funcionarios_elegiveis", 0),
            "valor_total_vr": agent_data.get("valor_total_vr", 0.0),
            "valor_empresa": agent_data.get("valor_empresa", 0.0),
            "valor_funcionario": agent_data.get("valor_funcionario", 0.0),
            "tempo_processamento": agent_data.get("tempo_processamento", "Unknown"),
            "arquivos_gerados": agent_data.get("arquivos_gerados", []),
            "validacoes": agent_data.get("validacoes", {}),
            "metodo_extracao": agent_data.get("metodo_extracao", "agente_analisador"),
            "log_sessao": session_id,
            "downloads_disponiveis": [
                {
                    "nome": "VR MENSAL 05.2025.xlsx",
                    "descricao": "Planilha principal com cálculos de VR",
                    "url": "/api/download/VR MENSAL 05.2025.xlsx",
                    "tipo": "excel"
                },
                {
                    "nome": "FUNCIONARIOS_EXCLUIDOS_AUDITORIA.xlsx",
                    "descricao": "Relatório de exclusões para auditoria",
                    "url": "/api/download/FUNCIONARIOS_EXCLUIDOS_AUDITORIA.xlsx",
                    "tipo": "excel"
                },
                {
                    "nome": log_filename,
                    "descricao": "Log completo das conversas dos agentes",
                    "url": f"/api/download/{log_filename}",
                    "tipo": "log"
                }
            ]
        })

    except Exception as e:
        print(f"❌ Erro crítico na API: {e}")
        # Tentar salvar log mesmo em caso de erro
        try:
            agent_logger_tool.func("log", f"ERRO: {str(e)}", "ERROR")
            agent_logger_tool.func("save", "", "ERROR_HANDLER")
        except:
            pass

        return jsonify({
            "status": "error",
            "error": f"Erro crítico: {str(e)}"
        }), 500



@app.route('/api/test-groq', methods=['GET'])
def test_groq():
    """Testa a conectividade com a API do Groq usando a chave padrão"""
    try:
        from tools.results_analyzer_agent_tool import get_llm

        print("🧪 Testando conexão com Groq...")

        # Tentar criar uma instância do LLM
        llm = get_llm()

        # Fazer uma chamada simples para testar
        from crewai import Agent, Task, Crew

        test_agent = Agent(
            role="Testador",
            goal="Responder um teste simples",
            backstory="Você é um agente de teste que responde '✅ GROQ_OK' para confirmar funcionamento.",
            llm=llm,
            verbose=False
        )

        test_task = Task(
            description="Responda apenas '✅ GROQ_OK' para confirmar que a API do Groq está funcionando.",
            expected_output="A string exata '✅ GROQ_OK'",
            agent=test_agent
        )

        crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=False
        )

        result = crew.kickoff()
        response_text = str(result).strip()

        print(f"🔧 Resposta do teste: {response_text}")

        # Verificar se a resposta contém a confirmação esperada
        success = "GROQ_OK" in response_text or "groq" in response_text.lower()

        return jsonify({
            "status": "success" if success else "warning",
            "groq_working": success,
            "message": "Chave API do Groq funcionando corretamente!" if success else "Resposta inesperada do Groq",
            "response": response_text,
            "api_key_partial": f"{os.getenv('GROQ_API_KEY', 'NONE')[:20]}..." if os.getenv('GROQ_API_KEY') else None
        })

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erro no teste do Groq: {error_msg}")

        return jsonify({
            "status": "error",
            "groq_working": False,
            "message": f"Erro ao testar Groq: {error_msg}",
            "error_type": type(e).__name__,
            "api_key_partial": f"{os.getenv('GROQ_API_KEY', 'NONE')[:20]}..." if os.getenv('GROQ_API_KEY') else None
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download de arquivo gerado"""
    try:
        # Obter diretório do projeto (pai da pasta api)
        api_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(api_dir)

        # Lista de possíveis localizações do arquivo
        possible_paths = [
            os.path.join(project_root, filename),  # Raiz do projeto
            os.path.join(api_dir, filename),  # Pasta api
            os.path.join(project_root, "output", filename),  # Subdiretório output
            os.path.join(project_root, app.config['UPLOAD_FOLDER'], filename),  # Upload folder
            os.path.join(project_root, "logs", filename)  # Logs folder
        ]

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            return jsonify({"error": f"Arquivo não encontrado: {filename}"}), 404
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": f"Erro no download: {str(e)}"}), 500


# Catch-all route para servir o React (deve ser a última rota)
@app.route('/<path:path>')
def serve_react_app(path):
    """Servir arquivos estáticos do React"""
    try:
        return app.send_static_file(path)
    except:
        # Se o arquivo não existe, servir o index.html (para React Router)
        return serve_frontend()


if __name__ == '__main__':
    # Obter porta do ambiente ou usar 5000 como padrão
    port = int(os.environ.get('PORT', 5000))

    print("🎯 FinaCrew API - Sistema VR/VA com Interface Web")
    print("📋 Suporte para frontend React e processamento FinaCrew")
    print(f"🚀 Iniciando servidor na porta {port}...")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )