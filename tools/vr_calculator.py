from crewai.tools import tool
import pandas as pd
from typing import Dict, Optional
from datetime import datetime
import numpy as np

@tool("calculate_vr_tool")
def calculate_vr_tool(employee_data: Dict[str, str]) -> str:
    """
    Calcula o valor de VR para um colaborador específico.
    
    Args:
        employee_data: Dicionário com dados do colaborador
            - matricula: Matrícula do colaborador
            - sindicato: Código do sindicato
            - dias_uteis: Dias úteis a considerar
            - valor_dia: Valor por dia do sindicato
    
    Returns:
        String com o cálculo detalhado
    """
    try:
        matricula = employee_data.get('matricula', '')
        sindicato = employee_data.get('sindicato', '')
        dias_uteis = int(employee_data.get('dias_uteis', 0))
        valor_dia = float(employee_data.get('valor_dia', 0))
        
        # Cálculo do valor total
        valor_total = dias_uteis * valor_dia
        valor_empresa = valor_total * 0.8
        valor_colaborador = valor_total * 0.2
        
        result = f"Cálculo VR - Matrícula {matricula}:\n"
        result += f"- Sindicato: {sindicato}\n"
        result += f"- Dias úteis: {dias_uteis}\n"
        result += f"- Valor por dia: R$ {valor_dia:.2f}\n"
        result += f"- Valor total: R$ {valor_total:.2f}\n"
        result += f"- Parte empresa (80%): R$ {valor_empresa:.2f}\n"
        result += f"- Parte colaborador (20%): R$ {valor_colaborador:.2f}\n"
        
        return result
        
    except Exception as e:
        return f"Erro no cálculo: {str(e)}"

@tool("calculate_working_days_tool")
def calculate_working_days_tool(month: int, year: int, union_code: str) -> str:
    """
    Calcula dias úteis do mês para um sindicato específico.
    
    Args:
        month: Mês (1-12)
        year: Ano
        union_code: Código do sindicato
    
    Returns:
        String com informação sobre dias úteis
    """
    try:
        # Simulação - em produção, buscar da base de dias úteis
        # Considerando média de 22 dias úteis por mês
        base_days = 22
        
        # Ajustes por sindicato (exemplo)
        union_adjustments = {
            'SIND001': 0,
            'SIND002': -1,  # Tem um feriado adicional
            'SIND003': 0,
        }
        
        adjustment = union_adjustments.get(union_code, 0)
        working_days = base_days + adjustment
        
        result = f"Dias úteis para {month:02d}/{year}:\n"
        result += f"- Sindicato: {union_code}\n"
        result += f"- Dias úteis base: {base_days}\n"
        result += f"- Ajuste sindicato: {adjustment:+d}\n"
        result += f"- Total dias úteis: {working_days}\n"
        
        return result
        
    except Exception as e:
        return f"Erro ao calcular dias úteis: {str(e)}"

@tool("batch_calculate_vr_tool")
def batch_calculate_vr_tool(input_file: str, output_file: str) -> str:
    """
    Calcula VR para todos os colaboradores de um arquivo.
    
    Args:
        input_file: Nome do arquivo com dados consolidados
        output_file: Nome do arquivo de saída
    
    Returns:
        String com resumo do processamento
    """
    try:
        # Carregar dados
        df = pd.read_pickle(f"/tmp/{input_file.replace('.xlsx', '')}_df.pkl")
        
        # Adicionar colunas de cálculo
        df['VALOR_TOTAL_VR'] = df['DIAS_UTEIS'] * df['VALOR_DIA_SINDICATO']
        df['VALOR_EMPRESA'] = df['VALOR_TOTAL_VR'] * 0.8
        df['VALOR_COLABORADOR'] = df['VALOR_TOTAL_VR'] * 0.2
        
        # Resumo
        total_colaboradores = len(df)
        valor_total = df['VALOR_TOTAL_VR'].sum()
        valor_medio = df['VALOR_TOTAL_VR'].mean()
        
        # Salvar resultado
        output_path = f"./output/{output_file}"
        df.to_excel(output_path, index=False)
        
        result = f"Cálculo em lote concluído:\n"
        result += f"- Total de colaboradores: {total_colaboradores}\n"
        result += f"- Valor total VR: R$ {valor_total:,.2f}\n"
        result += f"- Valor médio por colaborador: R$ {valor_medio:.2f}\n"
        result += f"- Arquivo salvo em: {output_path}\n"
        
        return result
        
    except Exception as e:
        return f"Erro no cálculo em lote: {str(e)}"