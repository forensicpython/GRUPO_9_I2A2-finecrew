#!/usr/bin/env python3
"""
Tool CrewAI para análise automática de planilhas de funcionários
Convertido para usar decorador @tool conforme filosofia Professor
"""

from crewai.tools import tool
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool("spreadsheet_analyzer_tool")
def spreadsheet_analyzer_tool(file_path: str, sheet_name: str = "default") -> str:
    """
    Analisa automaticamente planilhas de funcionários e identifica sua estrutura e tipo.

    Esta ferramenta identifica automaticamente se uma planilha contém dados de funcionários
    e classifica o tipo de lista (ATIVOS, FÉRIAS, DESLIGADOS, ADMISSÕES, etc.).

    Args:
        file_path: Caminho para o arquivo Excel ou CSV
        sheet_name: Nome da aba (opcional, usa primeira aba se não especificado)

    Returns:
        String com análise detalhada da planilha incluindo:
        - Tipo de planilha identificado
        - Estrutura de colunas encontrada
        - Quantidade de registros
        - Campos obrigatórios presentes/ausentes
        - Recomendações para processamento
    """
    try:
        print(f"📊 Analisando planilha: {file_path}")

        # Carregar arquivo
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"❌ Arquivo não encontrado: {file_path}"

        # Determinar método de carregamento
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        else:
            # Se sheet_name for "default" ou None, usar a primeira aba
            if sheet_name == "default" or sheet_name is None:
                df = pd.read_excel(file_path, sheet_name=0)  # Primeira aba
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

        if df.empty:
            return f"⚠️ Planilha vazia: {file_path}"

        # Padrões de identificação
        employee_patterns = {
            'matricula': ['matricula', 'matrícula', 'mat', 'codigo', 'código', 'id', 'registro', 'chapa'],
            'nome': ['nome', 'funcionario', 'funcionário', 'empregado', 'colaborador'],
            'cpf': ['cpf', 'documento', 'doc'],
            'sindicato': ['sindicato', 'sind', 'sindical', 'categoria'],
            'admissao': ['admissao', 'admissão', 'data_admissao', 'dt_admissao', 'ingresso'],
            'demissao': ['demissao', 'demissão', 'desligamento', 'saida', 'saída'],
            'ferias': ['ferias', 'férias', 'inicio', 'fim', 'periodo'],
            'salario': ['salario', 'salário', 'remuneracao', 'remuneração', 'valor']
        }

        # Normalizar nomes das colunas
        columns_normalized = [col.lower().strip() for col in df.columns]

        # Identificar campos presentes
        fields_found = {}
        for field_type, patterns in employee_patterns.items():
            for col in columns_normalized:
                if any(pattern in col for pattern in patterns):
                    fields_found[field_type] = df.columns[columns_normalized.index(col)]
                    break

        # Classificar tipo de planilha
        spreadsheet_type = "DESCONHECIDO"
        confidence = 0

        if 'demissao' in fields_found or any('deslig' in col for col in columns_normalized):
            spreadsheet_type = "DESLIGADOS"
            confidence = 90
        elif 'ferias' in fields_found or any('feria' in col for col in columns_normalized):
            spreadsheet_type = "FERIAS"
            confidence = 90
        elif 'admissao' in fields_found or any('admiss' in col for col in columns_normalized):
            spreadsheet_type = "ADMISSOES"
            confidence = 85
        elif 'sindicato' in fields_found and 'matricula' in fields_found:
            spreadsheet_type = "ATIVOS"
            confidence = 85
        elif len(fields_found) >= 3:
            spreadsheet_type = "FUNCIONARIOS_GERAL"
            confidence = 70

        # Verificar integridade dos dados
        total_rows = len(df)
        non_null_rows = df.dropna(how='all').shape[0]

        # Gerar relatório
        analysis_report = f"""
📊 ANÁLISE DE PLANILHA CONCLUÍDA

📂 Arquivo: {file_path_obj.name}
🎯 Tipo Identificado: {spreadsheet_type} (Confiança: {confidence}%)
📏 Registros: {total_rows} total, {non_null_rows} com dados válidos

🔍 CAMPOS IDENTIFICADOS:
"""

        for field_type, column_name in fields_found.items():
            analysis_report += f"   ✅ {field_type.upper()}: '{column_name}'\n"

        # Verificar campos obrigatórios por tipo
        required_fields = {
            "ATIVOS": ['matricula', 'nome', 'sindicato'],
            "DESLIGADOS": ['matricula', 'demissao'],
            "FERIAS": ['matricula', 'ferias'],
            "ADMISSOES": ['matricula', 'admissao']
        }

        if spreadsheet_type in required_fields:
            missing_fields = []
            for req_field in required_fields[spreadsheet_type]:
                if req_field not in fields_found:
                    missing_fields.append(req_field)

            if missing_fields:
                analysis_report += f"\n⚠️ CAMPOS OBRIGATÓRIOS AUSENTES: {', '.join(missing_fields)}\n"
            else:
                analysis_report += f"\n✅ TODOS OS CAMPOS OBRIGATÓRIOS PRESENTES\n"

        # Amostra de dados
        analysis_report += f"\n📋 AMOSTRA DE DADOS (primeiras 3 linhas):\n"
        sample_data = df.head(3).to_string(index=False, max_cols=6)
        analysis_report += f"{sample_data}\n"

        # Recomendações
        analysis_report += f"\n💡 RECOMENDAÇÕES:\n"
        if spreadsheet_type == "ATIVOS":
            analysis_report += "   - Use como base principal para consolidação\n"
            analysis_report += "   - Valide sindicatos contra tabela de valores\n"
        elif spreadsheet_type == "DESLIGADOS":
            analysis_report += "   - Aplicar regra do dia 15 para comunicados\n"
            analysis_report += "   - Calcular valores proporcionais\n"
        elif spreadsheet_type == "FERIAS":
            analysis_report += "   - Reduzir dias úteis para funcionários em férias\n"
        elif spreadsheet_type == "ADMISSOES":
            analysis_report += "   - Calcular valores proporcionais por data de admissão\n"

        analysis_report += f"\n✅ Análise concluída com sucesso!"

        print(analysis_report)
        return analysis_report

    except Exception as e:
        error_msg = f"❌ Erro na análise da planilha {file_path}: {str(e)}"
        print(error_msg)
        return error_msg