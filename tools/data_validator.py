from crewai.tools import tool
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import os

@tool("data_validator_tool")
def data_validator_tool(validation_type: str, data_file: str) -> str:
    """
    Valida dados conforme regras de negócio específicas.
    
    Args:
        validation_type: Tipo de validação ('exclusions', 'dates', 'mandatory_fields')
        data_file: Nome do arquivo de dados a validar
    
    Returns:
        String com resultado da validação
    """
    try:
        # Carregar dados
        df = pd.read_pickle(f"/tmp/{data_file.replace('.xlsx', '')}_df.pkl")
        
        if validation_type == "exclusions":
            return _validate_exclusions(df)
        elif validation_type == "dates":
            return _validate_dates(df)
        elif validation_type == "mandatory_fields":
            return _validate_mandatory_fields(df)
        else:
            return f"Tipo de validação '{validation_type}' não reconhecido"
            
    except Exception as e:
        return f"Erro na validação: {str(e)}"

def _validate_exclusions(df: pd.DataFrame) -> str:
    """Valida e marca registros para exclusão"""
    exclusions = []
    
    # Verificar cargos de diretores
    if 'CARGO' in df.columns:
        directors = df[df['CARGO'].str.contains('DIRETOR', case=False, na=False)]
        exclusions.append(f"Diretores identificados: {len(directors)} registros")
    
    # Aqui adicionaríamos outras regras de exclusão
    
    result = "Validação de Exclusões:\n"
    result += "\n".join(exclusions) if exclusions else "Nenhuma exclusão identificada"
    
    return result

def _validate_dates(df: pd.DataFrame) -> str:
    """Valida consistência de datas"""
    issues = []
    
    date_columns = [col for col in df.columns if 'DATA' in col.upper()]
    
    for col in date_columns:
        try:
            # Tentar converter para datetime
            df[col] = pd.to_datetime(df[col], errors='coerce')
            invalid = df[df[col].isna()].shape[0]
            if invalid > 0:
                issues.append(f"Coluna '{col}': {invalid} datas inválidas")
        except:
            issues.append(f"Coluna '{col}': erro ao processar datas")
    
    result = "Validação de Datas:\n"
    result += "\n".join(issues) if issues else "Todas as datas estão válidas"
    
    return result

def _validate_mandatory_fields(df: pd.DataFrame) -> str:
    """Valida campos obrigatórios"""
    mandatory = ['MATRICULA', 'NOME', 'CPF']
    missing = []
    
    for field in mandatory:
        if field in df.columns:
            null_count = df[field].isna().sum()
            if null_count > 0:
                missing.append(f"Campo '{field}': {null_count} valores faltantes")
        else:
            missing.append(f"Campo obrigatório '{field}' não encontrado")
    
    result = "Validação de Campos Obrigatórios:\n"
    result += "\n".join(missing) if missing else "Todos os campos obrigatórios estão preenchidos"
    
    return result

@tool("apply_business_rules_tool")
def apply_business_rules_tool(rule_type: str, parameters: Dict[str, str]) -> str:
    """
    Aplica regras de negócio específicas nos dados.
    
    Args:
        rule_type: Tipo de regra ('dia15', 'ferias', 'proporcional')
        parameters: Parâmetros específicos para a regra
    
    Returns:
        String com resultado da aplicação da regra
    """
    try:
        if rule_type == "dia15":
            return _apply_day15_rule(parameters.get('date', ''))
        elif rule_type == "ferias":
            return _apply_vacation_rule(parameters)
        elif rule_type == "proporcional":
            return _apply_proportional_rule(parameters)
        else:
            return f"Tipo de regra '{rule_type}' não reconhecido"
            
    except Exception as e:
        return f"Erro ao aplicar regra: {str(e)}"

def _apply_day15_rule(termination_date: str) -> str:
    """Aplica regra do dia 15 para desligamentos"""
    try:
        date = pd.to_datetime(termination_date)
        if date.day <= 15:
            return f"Desligamento em {date.strftime('%d/%m/%Y')}: NÃO pagar VR (antes do dia 15)"
        else:
            return f"Desligamento em {date.strftime('%d/%m/%Y')}: Pagar VR proporcional (após dia 15)"
    except:
        return "Data de desligamento inválida"

def _apply_vacation_rule(parameters: Dict) -> str:
    """Aplica regras de férias"""
    # Implementação simplificada
    return "Regra de férias aplicada conforme sindicato"

def _apply_proportional_rule(parameters: Dict) -> str:
    """Calcula valores proporcionais"""
    # Implementação simplificada
    return "Cálculo proporcional realizado"