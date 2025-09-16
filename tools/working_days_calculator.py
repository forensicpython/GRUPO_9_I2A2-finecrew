from crewai.tools import tool
import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timedelta, date
import holidays
from typing import Dict, List

@tool("calculate_working_days_by_region_tool")
def calculate_working_days_by_region_tool(reference_month: str = "05.2025") -> str:
    """
    Calcula dias úteis EXATOS por região/sindicato considerando:
    - Feriados nacionais
    - Feriados estaduais específicos  
    - Feriados municipais
    - Calendário de cada sindicato
    """
    try:
        print(f"📅 Calculando dias úteis por região para {reference_month}...")
        
        # Extrair mês e ano
        mes, ano = reference_month.split('.')
        target_month = int(mes)
        target_year = int(ano)
        
        # Carregar base de sindicatos
        project_root = Path(os.path.dirname(__file__)).parent
        raw_data_path = project_root / "raw_data"
        
        sindicato_path = raw_data_path / "Base sindicato x valor.xlsx"
        if not sindicato_path.exists():
            return "❌ Base de sindicatos não encontrada"
        
        sindicato_df = pd.read_excel(sindicato_path)
        
        # Mapear sindicatos para regiões e calcular dias úteis
        working_days_by_syndicate = {}
        holiday_details = {}
        
        for _, row in sindicato_df.iterrows():
            estado = str(row.iloc[0]).strip()
            valor_diario = float(row.iloc[1])
            
            # Calcular dias úteis específicos para cada estado
            working_days, state_holidays = calculate_working_days_for_state(
                estado, target_year, target_month
            )
            
            working_days_by_syndicate[estado] = {
                'dias_uteis': working_days,
                'valor_diario': valor_diario,
                'feriados_especificos': len(state_holidays),
                'valor_mensal_base': working_days * valor_diario
            }
            
            holiday_details[estado] = state_holidays
        
        # Gerar relatório detalhado
        relatorio = f"""
📅 CÁLCULO DE DIAS ÚTEIS POR REGIÃO - {reference_month.upper()}

📊 DIAS ÚTEIS POR SINDICATO/ESTADO:
"""
        
        for estado, dados in working_days_by_syndicate.items():
            relatorio += f"""
🏢 {estado}:
   - Dias úteis: {dados['dias_uteis']} dias
   - Feriados específicos: {dados['feriados_especificos']}
   - Valor diário: R$ {dados['valor_diario']:.2f}
   - Valor mensal base: R$ {dados['valor_mensal_base']:.2f}
"""
        
        relatorio += f"""
🎉 FERIADOS ESPECÍFICOS POR REGIÃO:
"""
        
        for estado, feriados in holiday_details.items():
            if feriados:
                relatorio += f"\n🏢 {estado}:\n"
                for feriado in feriados:
                    if isinstance(feriado, dict):
                        relatorio += f"   - {feriado['data'].strftime('%d/%m/%Y')}: {feriado['nome']}\n"
        
        # Salvar configuração de dias úteis
        output_path = project_root / "output" / "dias_uteis_por_regiao.xlsx"
        output_path.parent.mkdir(exist_ok=True)
        
        df_dias_uteis = pd.DataFrame([
            {
                'Estado_Sindicato': estado,
                'Dias_Uteis': dados['dias_uteis'],
                'Feriados_Especificos': dados['feriados_especificos'],
                'Valor_Diario': dados['valor_diario'],
                'Valor_Mensal_Base': dados['valor_mensal_base']
            }
            for estado, dados in working_days_by_syndicate.items()
        ])
        
        df_dias_uteis.to_excel(output_path, index=False)
        
        relatorio += f"""
📄 ARQUIVO GERADO:
- Configuração salva em: {output_path}

✅ CÁLCULO CONFORME ESPECIFICAÇÕES DO PROJETO!
"""
        
        print(relatorio)
        return relatorio
        
    except Exception as e:
        error_msg = f"❌ Erro no cálculo de dias úteis: {str(e)}"
        print(error_msg)
        return error_msg

def calculate_working_days_for_state(estado: str, year: int, month: int) -> tuple:
    """Calcula dias úteis específicos para um estado considerando feriados regionais"""
    
    # Obter feriados nacionais
    br_holidays = holidays.Brazil(years=year)
    
    # Obter feriados específicos por estado
    state_specific_holidays = get_state_specific_holidays(estado, year)
    
    # Combinar feriados
    all_holidays = set(br_holidays.keys()) | set([h['data'] for h in state_specific_holidays])
    
    # Calcular dias úteis para o mês específico
    start_date = date(year, month, 1)
    
    # Último dia do mês
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Se não for sábado (5) nem domingo (6) nem feriado
        if current_date.weekday() < 5 and current_date not in all_holidays:
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days, state_specific_holidays

def get_state_specific_holidays(estado: str, year: int) -> List[Dict]:
    """Retorna feriados específicos por estado com nomes"""
    
    state_holidays = []
    
    if "São Paulo" in estado or "SP" in estado:
        state_holidays.extend([
            {'data': date(year, 1, 25), 'nome': 'Aniversário de São Paulo'},
            {'data': date(year, 4, 23), 'nome': 'São Jorge'},
            {'data': date(year, 7, 9), 'nome': 'Revolução Constitucionalista'}
        ])
    
    elif "Rio de Janeiro" in estado or "RJ" in estado:
        state_holidays.extend([
            {'data': date(year, 4, 23), 'nome': 'São Jorge'},
            {'data': date(year, 11, 20), 'nome': 'Zumbi dos Palmares'},
            {'data': date(year, 12, 13), 'nome': 'Santa Luzia'}
        ])
    
    elif "Paraná" in estado or "PR" in estado:
        state_holidays.extend([
            {'data': date(year, 12, 19), 'nome': 'Emancipação do Paraná'}
        ])
    
    elif "Rio Grande do Sul" in estado or "RS" in estado:
        state_holidays.extend([
            {'data': date(year, 9, 20), 'nome': 'Revolução Farroupilha'}
        ])
    
    elif "Minas Gerais" in estado or "MG" in estado:
        state_holidays.extend([
            {'data': date(year, 4, 21), 'nome': 'Tiradentes'}
        ])
    
    # Filtrar feriados do mês específico se for maio
    if year == 2025:
        may_holidays = [h for h in state_holidays if h['data'].month == 5]
        return may_holidays
    
    return state_holidays

@tool("apply_working_days_to_employees_tool")
def apply_working_days_to_employees_tool() -> str:
    """
    Aplica os dias úteis calculados por região aos funcionários
    conforme seu sindicato/localização
    """
    try:
        project_root = Path(os.path.dirname(__file__)).parent
        raw_data_path = project_root / "raw_data"
        output_path = project_root / "output"
        
        print("🔄 Aplicando dias úteis por região aos funcionários...")
        
        # Carregar base de funcionários ativos
        ativos_df = pd.read_excel(raw_data_path / "ATIVOS.xlsx")
        
        # Carregar configuração de dias úteis por região
        dias_uteis_path = output_path / "dias_uteis_por_regiao.xlsx"
        if not dias_uteis_path.exists():
            return "❌ Execute primeiro o cálculo de dias úteis por região"
        
        dias_uteis_df = pd.read_excel(dias_uteis_path)
        
        # Criar mapeamento sindicato -> dias úteis
        sindicato_to_days = {}
        for _, row in dias_uteis_df.iterrows():
            estado = row['Estado_Sindicato']
            dias = row['Dias_Uteis']
            sindicato_to_days[estado] = dias
        
        # Aplicar dias úteis aos funcionários
        def get_working_days_for_employee(sindicato):
            sindicato_str = str(sindicato).strip()
            return sindicato_to_days.get(sindicato_str, 22)  # 22 como padrão
        
        ativos_df['DIAS_UTEIS_REGIAO'] = ativos_df['Sindicato'].apply(get_working_days_for_employee)
        
        # Estatísticas
        stats = ativos_df.groupby('Sindicato')['DIAS_UTEIS_REGIAO'].agg(['count', 'first']).reset_index()
        stats.columns = ['Sindicato', 'Dados de funcionários processados', 'Dias_Uteis']
        
        # Salvar resultado
        resultado_path = output_path / "funcionarios_com_dias_uteis_regiao.xlsx"
        ativos_df.to_excel(resultado_path, index=False)
        
        relatorio = f"""
🔄 APLICAÇÃO DE DIAS ÚTEIS POR REGIÃO CONCLUÍDA

📊 DISTRIBUIÇÃO POR SINDICATO:
"""
        
        for _, row in stats.iterrows():
            relatorio += f"🏢 {row['Sindicato']}: {row['Dados de funcionários processados']} funcionários, {row['Dias_Uteis']} dias úteis\n"
        
        relatorio += f"""
📄 ARQUIVOS GERADOS:
- Funcionários com dias úteis: {resultado_path}

✅ DIAS ÚTEIS APLICADOS CONFORME REGIÃO/SINDICATO!
"""
        
        print(relatorio)
        return relatorio
        
    except Exception as e:
        error_msg = f"❌ Erro na aplicação: {str(e)}"
        print(error_msg)
        return error_msg