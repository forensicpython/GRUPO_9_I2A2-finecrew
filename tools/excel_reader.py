from crewai.tools import tool
import pandas as pd
import os
from typing import Dict, List, Optional
from pathlib import Path

@tool("excel_reader_tool")
def excel_reader_tool(file_name: str, sheet_name: str = "") -> str:
    """
    Lê arquivos Excel da pasta raw_data e retorna os dados em formato estruturado.
    
    Args:
        file_name: Nome do arquivo Excel (ex: 'ATIVOS.xlsx')
        sheet_name: Nome da aba a ser lida. Use "" ou "Sheet1" para primeira aba
    
    Returns:
        String com informações sobre o arquivo lido ou erro
    """
    try:
        # Construir caminho do arquivo (considerando que está sendo chamado de src/)
        base_path_env = os.getenv('RAW_DATA_PATH', '../raw_data')
        base_path = Path(os.path.dirname(__file__)).parent / 'raw_data'
        file_path = base_path / file_name
        
        if not file_path.exists():
            return f"Erro: Arquivo '{file_name}' não encontrado em {base_path}"
        
        # Ler arquivo Excel
        # Tratar diferentes casos de sheet_name
        if sheet_name and sheet_name.strip() and sheet_name not in ["null", "None", "none", ""]:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            # Sem sheet_name especificado ou string vazia, ler primeira aba
            df = pd.read_excel(file_path)
        
        # Informações básicas sobre o arquivo
        info = f"Arquivo '{file_name}' lido com sucesso!\n"
        info += f"- Total de linhas: {len(df)}\n"
        info += f"- Total de colunas: {len(df.columns)}\n"
        info += f"- Colunas: {', '.join(df.columns.tolist())}\n"
        info += f"- Primeiras 5 linhas:\n{df.head().to_string()}\n"
        
        # Salvar DataFrame para uso posterior
        # Nota: Em produção, usar um sistema de cache mais robusto
        df.to_pickle(f"/tmp/{file_name.replace('.xlsx', '')}_df.pkl")
        
        return info
        
    except Exception as e:
        return f"Erro ao ler arquivo '{file_name}': {str(e)}"

@tool("list_excel_files_tool")
def list_excel_files_tool() -> str:
    """
    Lista todos os arquivos Excel disponíveis na pasta raw_data.
    
    Returns:
        String com lista de arquivos disponíveis
    """
    try:
        base_path = Path(os.path.dirname(__file__)).parent / 'raw_data'
        
        if not base_path.exists():
            return f"Erro: Pasta {base_path} não encontrada"
        
        excel_files = list(base_path.glob("*.xlsx"))
        
        if not excel_files:
            return "Nenhum arquivo Excel encontrado na pasta raw_data"
        
        info = "Arquivos Excel disponíveis:\n"
        for file in sorted(excel_files):
            size = file.stat().st_size / 1024  # KB
            info += f"- {file.name} ({size:.1f} KB)\n"
        
        return info
        
    except Exception as e:
        return f"Erro ao listar arquivos: {str(e)}"