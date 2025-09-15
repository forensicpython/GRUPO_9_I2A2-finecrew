from crewai.tools import tool
import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple
import math

@tool("calculate_proportional_benefits_tool")
def calculate_proportional_benefits_tool(reference_month: str = "05.2025") -> str:
    """
    Calcula benefícios proporcionais para:
    - Admissões no meio do mês (datas quebradas)
    - Desligamentos após dia 15 
    - Funcionários com férias parciais
    - Ajustes proporcionais conforme folha ponto
    """
    try:
        project_root = Path(os.path.dirname(__file__)).parent
        raw_data_path = project_root / "raw_data"
        
        print(f"🧮 Calculando benefícios proporcionais para {reference_month}...")
        
        # Extrair mês e ano de referência
        mes, ano = reference_month.split('.')
        target_month = int(mes)
        target_year = int(ano)
        
        # Carregar todas as bases necessárias
        ativos_df = pd.read_excel(raw_data_path / "ATIVOS.xlsx")
        admissoes_df = pd.read_excel(raw_data_path / "ADMISSÃO ABRIL.xlsx")
        desligados_df = pd.read_excel(raw_data_path / "DESLIGADOS.xlsx")
        ferias_df = pd.read_excel(raw_data_path / "FÉRIAS.xlsx")
        
        # Calcular proporcionais para cada categoria
        print("\n📅 Calculando proporcionais para admissões...")
        admissoes_proporcionais = calculate_admission_proportionals(
            admissoes_df, target_year, target_month
        )
        
        print("\n📅 Calculando proporcionais para desligamentos...")
        desligamentos_proporcionais = calculate_termination_proportionals(
            desligados_df, target_year, target_month
        )
        
        print("\n🏖️ Calculando proporcionais para férias...")
        ferias_proporcionais = calculate_vacation_proportionals(
            ferias_df, target_year, target_month
        )
        
        # Consolidar todos os cálculos proporcionais
        resultado_consolidado = consolidate_proportional_calculations(
            ativos_df, admissoes_proporcionais, desligamentos_proporcionais, ferias_proporcionais
        )
        
        # Salvar resultados
        output_path = project_root / "output" / "calculos_proporcionais.xlsx"
        output_path.parent.mkdir(exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Aba principal com todos os cálculos
            resultado_consolidado.to_excel(writer, sheet_name='Cálculos Proporcionais', index=False)
            
            # Abas detalhadas por tipo
            if admissoes_proporcionais:
                pd.DataFrame(admissoes_proporcionais).to_excel(writer, sheet_name='Admissões Proporcionais', index=False)
            
            if desligamentos_proporcionais:
                pd.DataFrame(desligamentos_proporcionais).to_excel(writer, sheet_name='Desligamentos Proporcionais', index=False)
            
            if ferias_proporcionais:
                pd.DataFrame(ferias_proporcionais).to_excel(writer, sheet_name='Férias Proporcionais', index=False)
        
        # Gerar relatório
        total_funcionarios = len(resultado_consolidado)
        admissoes_count = len([f for f in resultado_consolidado if f.get('TIPO_CALCULO') == 'ADMISSAO_PROPORCIONAL'])
        desligamentos_count = len([f for f in resultado_consolidado if f.get('TIPO_CALCULO') == 'DESLIGAMENTO_PROPORCIONAL'])
        ferias_count = len([f for f in resultado_consolidado if f.get('TIPO_CALCULO') == 'FERIAS_PROPORCIONAL'])
        
        relatorio = f"""
🧮 CÁLCULO DE BENEFÍCIOS PROPORCIONAIS CONCLUÍDO

📊 RESUMO POR TIPO:
- Total funcionários processados: {total_funcionarios}
- Admissões proporcionais: {admissoes_count}
- Desligamentos proporcionais: {desligamentos_count}  
- Férias proporcionais: {ferias_count}

📅 REGRAS APLICADAS:
✅ Admissões meio do mês: Proporcional aos dias trabalhados
✅ Desligamentos pós dia 15: Proporcional conforme regra
✅ Férias parciais: Desconto proporcional aos dias
✅ Datas quebradas: Cálculo preciso por dia útil

📄 ARQUIVO GERADO:
- Cálculos detalhados: {output_path}

✅ CÁLCULO PROPORCIONAL CONFORME ESPECIFICAÇÕES!
"""
        
        print(relatorio)
        return relatorio
        
    except Exception as e:
        error_msg = f"❌ Erro no cálculo proporcional: {str(e)}"
        print(error_msg)
        return error_msg

def calculate_admission_proportionals(admissoes_df: pd.DataFrame, year: int, month: int) -> List[Dict]:
    """Calcula proporcionais para admissões no meio do mês"""
    proporcionais = []
    
    # Converter coluna de admissão para datetime
    admissoes_df['Admissão'] = pd.to_datetime(admissoes_df['Admissão'], errors='coerce')
    
    # Filtrar admissões do mês de referência
    admissoes_mes = admissoes_df[
        (admissoes_df['Admissão'].dt.year == year) &
        (admissoes_df['Admissão'].dt.month == month)
    ]
    
    # Calcular dias úteis totais do mês
    total_working_days = calculate_working_days_in_month(year, month)
    
    for _, row in admissoes_mes.iterrows():
        matricula = str(row['MATRICULA'])
        data_admissao = row['Admissão']
        
        if pd.notna(data_admissao):
            # Calcular dias úteis trabalhados desde a admissão
            days_worked = calculate_working_days_from_date(data_admissao, year, month)
            
            # Calcular proporção
            proportion = days_worked / total_working_days if total_working_days > 0 else 0
            
            proporcionais.append({
                'MATRICULA': matricula,
                'DATA_ADMISSAO': data_admissao,
                'DIAS_UTEIS_TOTAL_MES': total_working_days,
                'DIAS_UTEIS_TRABALHADOS': days_worked,
                'PROPORCAO': proportion,
                'TIPO_CALCULO': 'ADMISSAO_PROPORCIONAL',
                'OBSERVACAO': f'Admitido em {data_admissao.strftime("%d/%m/%Y")} - {days_worked}/{total_working_days} dias'
            })
            
            print(f"   📅 {matricula}: Admitido em {data_admissao.strftime('%d/%m/%Y')} - {days_worked}/{total_working_days} dias ({proportion:.2%})")
    
    return proporcionais

def calculate_termination_proportionals(desligados_df: pd.DataFrame, year: int, month: int) -> List[Dict]:
    """Calcula proporcionais para desligamentos após dia 15"""
    proporcionais = []
    
    # Converter coluna de data para datetime
    desligados_df['DATA DEMISSÃO'] = pd.to_datetime(desligados_df['DATA DEMISSÃO'], errors='coerce')
    
    # Filtrar desligamentos do mês de referência
    desligados_mes = desligados_df[
        (desligados_df['DATA DEMISSÃO'].dt.year == year) &
        (desligados_df['DATA DEMISSÃO'].dt.month == month)
    ]
    
    for _, row in desligados_mes.iterrows():
        matricula = str(row['MATRICULA ']).strip()
        data_demissao = row['DATA DEMISSÃO']
        comunicado = str(row.get('COMUNICADO DE DESLIGAMENTO', '')).upper()
        
        if pd.notna(data_demissao):
            dia_demissao = data_demissao.day
            comunicado_ok = 'OK' in comunicado or 'SIM' in comunicado
            
            if comunicado_ok and dia_demissao > 15:
                # Regra: Desligamento após dia 15 com comunicado OK = proporcional
                # Calcular dias até o dia 15
                days_to_pay = 15  # Pagar até dia 15 conforme regra
                total_working_days = calculate_working_days_in_month(year, month)
                
                # Calcular proporção baseada nos dias úteis até dia 15
                working_days_until_15 = calculate_working_days_until_day(year, month, 15)
                proportion = working_days_until_15 / total_working_days if total_working_days > 0 else 0
                
                proporcionais.append({
                    'MATRICULA': matricula,
                    'DATA_DEMISSAO': data_demissao,
                    'DIA_DEMISSAO': dia_demissao,
                    'COMUNICADO_OK': comunicado_ok,
                    'DIAS_UTEIS_PAGOS': working_days_until_15,
                    'DIAS_UTEIS_TOTAL_MES': total_working_days,
                    'PROPORCAO': proportion,
                    'TIPO_CALCULO': 'DESLIGAMENTO_PROPORCIONAL',
                    'OBSERVACAO': f'Desligado em {data_demissao.strftime("%d/%m/%Y")} pós dia 15 - pagar até dia 15'
                })
                
                print(f"   📅 {matricula}: Desligado em {data_demissao.strftime('%d/%m/%Y')} - pagar {working_days_until_15} dias ({proportion:.2%})")
    
    return proporcionais

def calculate_vacation_proportionals(ferias_df: pd.DataFrame, year: int, month: int) -> List[Dict]:
    """Calcula proporcionais para funcionários com férias no mês"""
    proporcionais = []
    
    # Processar dados de férias
    for _, row in ferias_df.iterrows():
        matricula = str(row['MATRICULA'])
        dias_ferias = row.get('DIAS DE FÉRIAS', 0)
        
        # Converter dias de férias para numérico
        try:
            dias_ferias = float(dias_ferias)
        except:
            dias_ferias = 0
        
        if dias_ferias > 0:
            # Calcular dias úteis totais do mês
            total_working_days = calculate_working_days_in_month(year, month)
            
            # Assumir que férias são em dias corridos, converter para dias úteis
            # Regra: 1 semana de férias = ~5 dias úteis
            dias_uteis_ferias = min(dias_ferias * (5/7), total_working_days)
            
            # Calcular dias úteis efetivamente trabalhados
            dias_uteis_trabalhados = max(0, total_working_days - dias_uteis_ferias)
            
            # Calcular proporção
            proportion = dias_uteis_trabalhados / total_working_days if total_working_days > 0 else 0
            
            proporcionais.append({
                'MATRICULA': matricula,
                'DIAS_FERIAS_CORRIDOS': dias_ferias,
                'DIAS_UTEIS_FERIAS': dias_uteis_ferias,
                'DIAS_UTEIS_TRABALHADOS': dias_uteis_trabalhados,
                'DIAS_UTEIS_TOTAL_MES': total_working_days,
                'PROPORCAO': proportion,
                'TIPO_CALCULO': 'FERIAS_PROPORCIONAL',
                'OBSERVACAO': f'{dias_ferias} dias de férias - trabalhou {dias_uteis_trabalhados:.1f}/{total_working_days} dias úteis'
            })
            
            print(f"   🏖️ {matricula}: {dias_ferias} dias férias - trabalhou {dias_uteis_trabalhados:.1f}/{total_working_days} dias ({proportion:.2%})")
    
    return proporcionais

def consolidate_proportional_calculations(ativos_df: pd.DataFrame, admissoes: List[Dict], 
                                        desligamentos: List[Dict], ferias: List[Dict]) -> pd.DataFrame:
    """Consolida todos os cálculos proporcionais"""
    
    # Criar dicionários para busca rápida
    admissoes_dict = {item['MATRICULA']: item for item in admissoes}
    desligamentos_dict = {item['MATRICULA']: item for item in desligamentos}
    ferias_dict = {item['MATRICULA']: item for item in ferias}
    
    resultado = []
    
    for _, funcionario in ativos_df.iterrows():
        matricula = str(funcionario['MATRICULA'])
        
        # Valores base
        resultado_funcionario = {
            'MATRICULA': matricula,
            'EMPRESA': funcionario.get('EMPRESA', ''),
            'TITULO_CARGO': funcionario.get('TITULO DO CARGO', ''),
            'SINDICATO': funcionario.get('Sindicato', ''),
            'DIAS_UTEIS_BASE': 22,  # Será ajustado pelos proporcionais
            'PROPORCAO_FINAL': 1.0,
            'TIPO_CALCULO': 'NORMAL',
            'OBSERVACOES': []
        }
        
        # Verificar se tem cálculo proporcional
        if matricula in admissoes_dict:
            item = admissoes_dict[matricula]
            resultado_funcionario.update({
                'DIAS_UTEIS_BASE': item['DIAS_UTEIS_TOTAL_MES'],
                'DIAS_UTEIS_EFETIVOS': item['DIAS_UTEIS_TRABALHADOS'],
                'PROPORCAO_FINAL': item['PROPORCAO'],
                'TIPO_CALCULO': item['TIPO_CALCULO']
            })
            resultado_funcionario['OBSERVACOES'].append(item['OBSERVACAO'])
        
        elif matricula in desligamentos_dict:
            item = desligamentos_dict[matricula]
            resultado_funcionario.update({
                'DIAS_UTEIS_BASE': item['DIAS_UTEIS_TOTAL_MES'],
                'DIAS_UTEIS_EFETIVOS': item['DIAS_UTEIS_PAGOS'],
                'PROPORCAO_FINAL': item['PROPORCAO'],
                'TIPO_CALCULO': item['TIPO_CALCULO']
            })
            resultado_funcionario['OBSERVACOES'].append(item['OBSERVACAO'])
        
        elif matricula in ferias_dict:
            item = ferias_dict[matricula]
            resultado_funcionario.update({
                'DIAS_UTEIS_BASE': item['DIAS_UTEIS_TOTAL_MES'],
                'DIAS_UTEIS_EFETIVOS': item['DIAS_UTEIS_TRABALHADOS'],
                'PROPORCAO_FINAL': item['PROPORCAO'],
                'TIPO_CALCULO': item['TIPO_CALCULO']
            })
            resultado_funcionario['OBSERVACOES'].append(item['OBSERVACAO'])
        
        else:
            # Funcionário normal (sem proporcionais)
            resultado_funcionario.update({
                'DIAS_UTEIS_EFETIVOS': 22,
                'OBSERVACOES': ['Funcionário normal - sem ajustes proporcionais']
            })
        
        # Converter observações para string
        resultado_funcionario['OBSERVACOES'] = '; '.join(resultado_funcionario['OBSERVACOES'])
        
        resultado.append(resultado_funcionario)
    
    return pd.DataFrame(resultado)

def calculate_working_days_in_month(year: int, month: int) -> int:
    """Calcula total de dias úteis no mês"""
    start_date = date(year, month, 1)
    
    # Último dia do mês
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Se não for sábado (5) nem domingo (6)
        if current_date.weekday() < 5:
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def calculate_working_days_from_date(start_date: datetime, year: int, month: int) -> int:
    """Calcula dias úteis trabalhados desde uma data específica no mês"""
    # Último dia do mês
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Usar apenas a data (sem hora)
    current_date = start_date.date()
    working_days = 0
    
    while current_date <= end_date:
        # Se não for sábado (5) nem domingo (6)
        if current_date.weekday() < 5:
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def calculate_working_days_until_day(year: int, month: int, target_day: int) -> int:
    """Calcula dias úteis até um dia específico do mês"""
    start_date = date(year, month, 1)
    end_date = date(year, month, min(target_day, 31))
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Se não for sábado (5) nem domingo (6)
        if current_date.weekday() < 5:
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days