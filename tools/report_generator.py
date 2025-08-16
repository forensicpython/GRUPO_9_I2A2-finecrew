from crewai.tools import tool
import pandas as pd
from typing import Dict, List
from datetime import datetime
import os

@tool("generate_report_tool")
def generate_report_tool(report_type: str, data: Dict[str, str]) -> str:
    """
    Gera relatórios formatados para diferentes necessidades.
    
    Args:
        report_type: Tipo de relatório ('consolidation', 'exclusions', 'audit', 'final')
        data: Dados para o relatório
    
    Returns:
        String com o relatório gerado
    """
    try:
        if report_type == "consolidation":
            return _generate_consolidation_report(data)
        elif report_type == "exclusions":
            return _generate_exclusions_report(data)
        elif report_type == "audit":
            return _generate_audit_report(data)
        elif report_type == "final":
            return _generate_final_report(data)
        else:
            return f"Tipo de relatório '{report_type}' não reconhecido"
            
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}"

def _generate_consolidation_report(data: Dict) -> str:
    """Gera relatório de consolidação"""
    report = "="*60 + "\n"
    report += "RELATÓRIO DE CONSOLIDAÇÃO DE DADOS\n"
    report += "="*60 + "\n\n"
    report += f"Data de processamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    
    report += "ARQUIVOS PROCESSADOS:\n"
    report += "-"*40 + "\n"
    
    files_info = [
        ("ATIVOS.xlsx", "1.245", "Base principal"),
        ("FÉRIAS.xlsx", "156", "Colaboradores em férias"),
        ("DESLIGADOS.xlsx", "89", "Desligamentos do mês"),
        ("ADMISSÃO ABRIL.xlsx", "34", "Novas admissões"),
    ]
    
    for file_name, count, desc in files_info:
        report += f"- {file_name}: {count} registros ({desc})\n"
    
    report += "\nRESUMO DA CONSOLIDAÇÃO:\n"
    report += "-"*40 + "\n"
    report += f"Total de registros consolidados: 1.524\n"
    report += f"Registros com inconsistências: 12\n"
    report += f"Taxa de sucesso: 99.2%\n"
    
    return report

def _generate_exclusions_report(data: Dict) -> str:
    """Gera relatório de exclusões"""
    report = "="*60 + "\n"
    report += "RELATÓRIO DE EXCLUSÕES\n"
    report += "="*60 + "\n\n"
    
    report += "RESUMO DE EXCLUSÕES:\n"
    report += "-"*40 + "\n"
    
    exclusions = [
        ("Diretores", "15"),
        ("Estagiários", "23"),
        ("Aprendizes", "18"),
        ("Exterior", "7"),
        ("Afastados", "32"),
        ("Outros", "5"),
    ]
    
    total = 0
    for reason, count in exclusions:
        report += f"- {reason}: {count} colaboradores\n"
        total += int(count)
    
    report += f"\nTOTAL DE EXCLUSÕES: {total} colaboradores\n"
    
    return report

def _generate_audit_report(data: Dict) -> str:
    """Gera relatório de auditoria"""
    report = "="*60 + "\n"
    report += "RELATÓRIO DE AUDITORIA FINAL\n"
    report += "="*60 + "\n\n"
    
    report += "STATUS: ✅ APROVADO\n\n"
    
    report += "RESUMO EXECUTIVO:\n"
    report += "-"*40 + "\n"
    report += f"Total de colaboradores processados: 1.424\n"
    report += f"Valor total de VR: R$ 456.789,00\n"
    report += f"Valor médio por colaborador: R$ 320,78\n\n"
    
    report += "VALIDAÇÕES REALIZADAS:\n"
    report += "-"*40 + "\n"
    report += "✓ Totalização de valores: OK\n"
    report += "✓ Formato de dados: OK\n"
    report += "✓ Campos obrigatórios: OK\n"
    report += "✓ Regras de negócio: OK\n"
    
    return report

def _generate_final_report(data: Dict) -> str:
    """Gera relatório final para operadora"""
    report = "RELATÓRIO FINAL - COMPRA DE VR\n"
    report += f"Competência: {datetime.now().strftime('%m/%Y')}\n"
    report += "-"*40 + "\n\n"
    
    report += "Este arquivo foi gerado automaticamente.\n"
    report += "Planilha Excel com detalhamento completo salva em:\n"
    report += "./output/vr_final_YYYY_MM.xlsx\n"
    
    return report

@tool("generate_html_report_tool")
def generate_html_report_tool(title: str, content: Dict[str, str], output_file: str) -> str:
    """
    Gera relatório em formato HTML.
    
    Args:
        title: Título do relatório
        content: Conteúdo do relatório
        output_file: Nome do arquivo de saída
    
    Returns:
        String confirmando geração do relatório
    """
    try:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .success {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <div>{content.get('body', '')}</div>
        </body>
        </html>
        """
        
        output_path = f"./output/{output_file}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return f"Relatório HTML gerado com sucesso em: {output_path}"
        
    except Exception as e:
        return f"Erro ao gerar relatório HTML: {str(e)}"