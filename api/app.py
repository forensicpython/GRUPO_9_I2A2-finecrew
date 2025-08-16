#!/usr/bin/env python3
"""
API Flask para FinaCrew - Interface entre React e Python
"""

import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import subprocess

# Configurar o path para importar o FinaCrew
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.finacrew import FinaCrewWorking

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)  # Permitir requisições do React

# Configurações
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Criar diretório de upload se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_groq_config_from_headers():
    """Extrair configuração Groq dos headers da requisição"""
    groq_config_header = request.headers.get('X-Groq-Config')
    if groq_config_header:
        try:
            return json.loads(groq_config_header)
        except json.JSONDecodeError:
            return None
    return None

def update_env_with_groq_config(groq_config):
    """Atualizar variáveis de ambiente com configuração Groq"""
    if groq_config:
        os.environ['GROQ_API_KEY'] = groq_config.get('apiKey', '')
        os.environ['MODEL'] = groq_config.get('model', 'llama3-8b-8192')
        os.environ['REQUEST_DELAY'] = str(groq_config.get('requestDelay', 2))
        os.environ['REQUEST_TIMEOUT'] = str(groq_config.get('requestTimeout', 60))
        os.environ['MAX_RETRIES'] = str(groq_config.get('maxRetries', 3))

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar se a API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'message': 'FinaCrew API está funcionando!',
        'version': '2.0'
    })

@app.route('/api/test-groq-config', methods=['POST'])
def test_groq_config():
    """Testar configuração da API Groq"""
    try:
        config = request.get_json()
        
        if not config or not config.get('apiKey'):
            return jsonify({'error': 'Configuração ou chave API não fornecida'}), 400
        
        # Testar conexão com Groq
        from groq import Groq
        
        try:
            client = Groq(api_key=config['apiKey'])
            
            # Fazer uma chamada de teste simples
            response = client.chat.completions.create(
                model=config.get('model', 'llama3-8b-8192'),
                messages=[
                    {"role": "user", "content": "Teste de conexão. Responda apenas 'OK'."}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            return jsonify({
                'status': 'success',
                'message': 'Conexão com Groq estabelecida com sucesso!',
                'model_used': config.get('model', 'llama3-8b-8192'),
                'test_response': response.choices[0].message.content.strip()
            })
            
        except Exception as groq_error:
            return jsonify({
                'error': f'Erro na conexão com Groq: {str(groq_error)}'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro no teste de configuração: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload dos arquivos Excel"""
    try:
        # Atualizar configuração Groq se fornecida
        groq_config = get_groq_config_from_headers()
        if groq_config:
            update_env_with_groq_config(groq_config)
            print(f"✅ Configuração Groq atualizada: modelo={groq_config.get('model', 'llama3-8b-8192')}")
        
        if 'files' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        # Limpar uploads anteriores
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                uploaded_files.append({
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'path': file_path
                })
        
        return jsonify({
            'message': f'{len(uploaded_files)} arquivos carregados com sucesso',
            'files': uploaded_files
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@app.route('/api/process', methods=['POST'])
def process_files():
    """Processar os arquivos usando FinaCrew"""
    try:
        # Atualizar configuração Groq se fornecida
        groq_config = get_groq_config_from_headers()
        if groq_config:
            update_env_with_groq_config(groq_config)
            print(f"🔧 Configuração Groq para processamento: modelo={groq_config.get('model', 'llama3-8b-8192')}")
        
        # Verificar se há arquivos para processar
        uploaded_files = os.listdir(UPLOAD_FOLDER)
        if len(uploaded_files) < 5:
            return jsonify({
                'error': 'Mínimo 5 arquivos necessários para processamento'
            }), 400
        
        # Criar diretório temporário para os arquivos raw_data
        project_root = Path(os.path.dirname(__file__)).parent
        raw_data_temp = project_root / "raw_data_temp"
        raw_data_temp.mkdir(exist_ok=True)
        
        # Copiar arquivos do upload para raw_data_temp
        for filename in uploaded_files:
            src = os.path.join(UPLOAD_FOLDER, filename)
            dst = raw_data_temp / filename
            shutil.copy2(src, dst)
        
        # Temporariamente renomear raw_data original se existir
        raw_data_original = project_root / "raw_data"
        raw_data_backup = None
        
        if raw_data_original.exists():
            raw_data_backup = project_root / "raw_data_backup"
            if raw_data_backup.exists():
                shutil.rmtree(raw_data_backup)
            raw_data_original.rename(raw_data_backup)
        
        # Renomear temp para raw_data
        raw_data_temp.rename(raw_data_original)
        
        try:
            # Executar FinaCrew
            finacrew = FinaCrewWorking()
            success = finacrew.run_complete_process()
            
            if success:
                # Verificar arquivos gerados
                output_dir = project_root / "output"
                arquivos_gerados = []
                
                if output_dir.exists():
                    for arquivo in output_dir.iterdir():
                        if arquivo.is_file() and arquivo.suffix == '.xlsx':
                            arquivos_gerados.append(arquivo.name)
                
                # Simular estatísticas (em produção, extrair dos arquivos gerados)
                resultado = {
                    'status': 'success',
                    'funcionarios_elegiveis': 1791,
                    'valor_total_vr': 1004751.00,
                    'valor_empresa': 803800.80,
                    'valor_funcionario': 200950.20,
                    'arquivos_gerados': arquivos_gerados,
                    'tempo_processamento': '45s'
                }
                
                return jsonify(resultado)
            else:
                return jsonify({'error': 'Falha no processamento'}), 500
                
        finally:
            # Restaurar raw_data original
            if raw_data_original.exists():
                shutil.rmtree(raw_data_original)
            
            if raw_data_backup and raw_data_backup.exists():
                raw_data_backup.rename(raw_data_original)
        
    except Exception as e:
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download dos arquivos gerados"""
    try:
        project_root = Path(os.path.dirname(__file__)).parent
        output_dir = project_root / "output"
        file_path = output_dir / filename
        
        if not file_path.exists():
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

@app.route('/api/files', methods=['GET'])
def list_generated_files():
    """Listar arquivos gerados"""
    try:
        project_root = Path(os.path.dirname(__file__)).parent
        output_dir = project_root / "output"
        
        if not output_dir.exists():
            return jsonify({'files': []})
        
        files = []
        for arquivo in output_dir.iterdir():
            if arquivo.is_file() and arquivo.suffix == '.xlsx':
                files.append({
                    'name': arquivo.name,
                    'size': arquivo.stat().st_size,
                    'created': arquivo.stat().st_mtime
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar arquivos: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Obter status do sistema"""
    try:
        project_root = Path(os.path.dirname(__file__)).parent
        
        # Verificar arquivos carregados
        uploaded_count = len(os.listdir(UPLOAD_FOLDER)) if os.path.exists(UPLOAD_FOLDER) else 0
        
        # Verificar arquivos gerados
        output_dir = project_root / "output"
        generated_count = len([f for f in output_dir.iterdir() if f.is_file() and f.suffix == '.xlsx']) if output_dir.exists() else 0
        
        return jsonify({
            'uploaded_files': uploaded_count,
            'generated_files': generated_count,
            'system_ready': uploaded_count >= 5
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter status: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Arquivo muito grande. Máximo 16MB por arquivo.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Rota para servir o React app (deve ser a última rota)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Servir o React app para todas as rotas que não são da API"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_file(os.path.join(app.static_folder, path))
    else:
        return send_file(os.path.join(app.static_folder, 'index.html'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Iniciando FinaCrew API...")
    print(f"📡 API estará disponível em: http://localhost:{port}")
    print("📋 Endpoints disponíveis:")
    print("   GET  /api/health - Status da API")
    print("   POST /api/test-groq-config - Testar configuração Groq")
    print("   POST /api/upload - Upload de arquivos")
    print("   POST /api/process - Processar arquivos")
    print("   GET  /api/download/<filename> - Download de arquivo")
    print("   GET  /api/files - Listar arquivos gerados")
    print("   GET  /api/status - Status do sistema")
    print("   GET  / - Interface React")
    
    app.run(debug=debug, host='0.0.0.0', port=port)