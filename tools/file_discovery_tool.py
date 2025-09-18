#!/usr/bin/env python3
"""
Tool CrewAI para descoberta automática de arquivos na temp_uploads
Resolve o problema de mapeamento de arquivos para seus tipos corretos
"""

from crewai.tools import tool
import os
from pathlib import Path
from typing import Dict, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool("file_discovery_tool")
def file_discovery_tool(base_directory: str = "temp_uploads") -> str:
    """
    Descobre automaticamente todos os arquivos Excel disponíveis no diretório especificado
    e mapeia para suas categorias corretas baseado em nomes e padrões.

    Esta ferramenta resolve o problema de localização de arquivos quando eles podem ter
    nomes ligeiramente diferentes ou estar em diretórios específicos.

    Args:
        base_directory: Diretório base para buscar arquivos (padrão: temp_uploads)

    Returns:
        String com mapeamento completo de arquivos encontrados e suas categorias,
        incluindo caminhos completos e tipos identificados.
    """
    try:
        print(f"🔍 Descobrindo arquivos em: {base_directory}")

        # Verificar se diretório existe
        base_path = Path(base_directory)
        if not base_path.exists():
            return f"❌ Diretório não encontrado: {base_directory}"

        # Padrões para identificação de tipos de arquivo
        file_patterns = {
            'ATIVOS': ['ativo', 'employee', 'funcionario', 'colaborador'],
            'DESLIGADOS': ['desligado', 'demitido', 'deslig', 'terminated'],
            'FERIAS': ['feria', 'vacation', 'holiday'],
            'ADMISSOES': ['admiss', 'admission', 'hire', 'abril'],
            'SINDICATO_VALORES': ['sindicato', 'valor', 'union', 'value'],
            'ESTAGIO': ['estag', 'intern', 'trainee'],
            'EXTERIOR': ['exterior', 'external', 'overseas'],
            'AFASTAMENTOS': ['afastamento', 'leave', 'absence'],
            'APRENDIZ': ['aprendiz', 'apprentice'],
            'DIAS_UTEIS': ['dias', 'util', 'working', 'business'],
            'VR_MENSAL': ['vr', 'mensal', 'monthly', 'meal']
        }

        # Buscar todos os arquivos Excel
        excel_files = []
        for extension in ['*.xlsx', '*.xls']:
            excel_files.extend(base_path.glob(extension))

        if not excel_files:
            return f"⚠️ Nenhum arquivo Excel encontrado em: {base_directory}"

        # Classificar arquivos
        file_mapping = {}
        unclassified_files = []

        for file_path in excel_files:
            file_name_lower = file_path.name.lower()
            classified = False

            for file_type, patterns in file_patterns.items():
                if any(pattern in file_name_lower for pattern in patterns):
                    if file_type not in file_mapping:
                        file_mapping[file_type] = []
                    file_mapping[file_type].append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2)
                    })
                    classified = True
                    break

            if not classified:
                unclassified_files.append({
                    'path': str(file_path),
                    'name': file_path.name,
                    'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2)
                })

        # Gerar relatório de descoberta
        discovery_report = f"""
🔍 RELATÓRIO DE DESCOBERTA DE ARQUIVOS

📂 Diretório analisado: {base_directory}
📊 Total de arquivos Excel encontrados: {len(excel_files)}

📋 ARQUIVOS CLASSIFICADOS POR CATEGORIA:
"""

        # Mapear para nomes esperados pelo sistema
        expected_mapping = {
            'ATIVOS': 'ATIVOS.xlsx',
            'DESLIGADOS': 'DESLIGADOS.xlsx',
            'FERIAS': 'FERIAS.xlsx',
            'ADMISSOES': 'ADMISSAO_ABRIL.xlsx',
            'SINDICATO_VALORES': 'Base_sindicato_x_valor.xlsx'
        }

        for file_type, files in file_mapping.items():
            discovery_report += f"\n🏷️ {file_type}:\n"
            for file_info in files:
                discovery_report += f"   ✅ {file_info['name']} ({file_info['size_mb']} MB)\n"
                discovery_report += f"      Caminho: {file_info['path']}\n"

        if unclassified_files:
            discovery_report += f"\n❓ ARQUIVOS NÃO CLASSIFICADOS:\n"
            for file_info in unclassified_files:
                discovery_report += f"   📄 {file_info['name']} ({file_info['size_mb']} MB)\n"
                discovery_report += f"      Caminho: {file_info['path']}\n"

        # Gerar instruções de uso
        discovery_report += f"\n💡 INSTRUÇÕES PARA AGENTES:\n"
        discovery_report += f"Para processar os arquivos, use os seguintes caminhos:\n\n"

        for file_type, files in file_mapping.items():
            if file_type in expected_mapping and files:
                primary_file = files[0]  # Usar o primeiro arquivo encontrado
                discovery_report += f"• {expected_mapping[file_type]} → use: {primary_file['path']}\n"

        discovery_report += f"\n✅ Descoberta de arquivos concluída!"
        discovery_report += f"\nUse sempre os caminhos completos fornecidos acima para acessar os arquivos."

        print(discovery_report)
        return discovery_report

    except Exception as e:
        error_msg = f"❌ Erro na descoberta de arquivos: {str(e)}"
        print(error_msg)
        return error_msg