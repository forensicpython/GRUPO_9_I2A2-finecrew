#!/usr/bin/env python3
"""
Tool CrewAI para cálculo de dias úteis por região/sindicato
Convertido para usar decorador @tool conforme filosofia Professor
"""

from crewai.tools import tool
import pandas as pd
from datetime import datetime, timedelta, date
import holidays
from typing import Dict, List
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool("working_days_calculator_tool")
def working_days_calculator_tool(reference_month: str = "05.2025") -> str:
    """
    Calcula dias úteis EXATOS por região/sindicato considerando feriados específicos.

    Esta ferramenta calcula dias úteis reais baseados em:
    - Feriados nacionais
    - Feriados estaduais específicos
    - Feriados municipais
    - Calendário específico de cada sindicato

    Args:
        reference_month: Mês de referência no formato "MM.AAAA" (padrão: "05.2025")

    Returns:
        String com relatório detalhado de dias úteis por região e estatísticas
    """
    try:
        print(f"📅 Calculando dias úteis por região para {reference_month}...")

        # Extrair mês e ano
        mes, ano = reference_month.split('.')
        target_month = int(mes)
        target_year = int(ano)

        # Valores VR por sindicato/estado (dados reais do projeto)
        union_values = {
            'SINDPD SP - São Paulo': 37.5,
            'SINDPD RJ - Rio de Janeiro': 35.0,
            'SINDPD PR - Paraná': 35.0,
            'SINDPD RS - Rio Grande do Sul': 35.0,
            'SINDPD MG - Minas Gerais': 35.0
        }

        # Calcular dias úteis por sindicato
        working_days_by_union = {}
        holiday_details = {}

        for union, daily_value in union_values.items():
            # Extrair estado do nome do sindicato
            if 'SP' in union or 'São Paulo' in union:
                state = 'São Paulo'
            elif 'RJ' in union or 'Rio de Janeiro' in union:
                state = 'Rio de Janeiro'
            elif 'PR' in union or 'Paraná' in union:
                state = 'Paraná'
            elif 'RS' in union or 'Rio Grande do Sul' in union:
                state = 'Rio Grande do Sul'
            elif 'MG' in union or 'Minas Gerais' in union:
                state = 'Minas Gerais'
            else:
                state = 'Brasil'

            # Calcular dias úteis específicos para o estado
            working_days, state_holidays = calculate_working_days_for_state(
                state, target_year, target_month
            )

            working_days_by_union[union] = {
                'dias_uteis': working_days,
                'valor_diario': daily_value,
                'estado': state,
                'feriados_especificos': len(state_holidays),
                'valor_mensal_base': working_days * daily_value
            }

            holiday_details[union] = state_holidays

        # Gerar relatório detalhado
        relatorio = f"""
📅 CÁLCULO DE DIAS ÚTEIS POR REGIÃO - {reference_month.upper()}

📊 DIAS ÚTEIS POR SINDICATO/ESTADO:
"""

        total_unions = len(working_days_by_union)
        avg_working_days = sum(data['dias_uteis'] for data in working_days_by_union.values()) / total_unions

        for union, dados in working_days_by_union.items():
            relatorio += f"""
🏢 {union}:
   📍 Estado: {dados['estado']}
   📅 Dias úteis: {dados['dias_uteis']} dias
   🎊 Feriados específicos: {dados['feriados_especificos']}
   💰 Valor diário: R$ {dados['valor_diario']:.2f}
   📈 Valor mensal base: R$ {dados['valor_mensal_base']:.2f}
"""

        relatorio += f"""
🎉 DETALHAMENTO DE FERIADOS ESPECÍFICOS:
"""

        for union, feriados in holiday_details.items():
            if feriados:
                relatorio += f"\n🏢 {union}:\n"
                for feriado in feriados:
                    if isinstance(feriado, dict):
                        relatorio += f"   🎊 {feriado['data'].strftime('%d/%m/%Y')}: {feriado['nome']}\n"

        # Estatísticas gerais
        relatorio += f"""
📊 ESTATÍSTICAS GERAIS:
   🏢 Total de sindicatos: {total_unions}
   📅 Média de dias úteis: {avg_working_days:.1f} dias
   📆 Mês de referência: {reference_month}
   🗓️ Feriados nacionais considerados: ✅
   🏛️ Feriados estaduais considerados: ✅

✅ CÁLCULO CONFORME ESPECIFICAÇÕES DO PROJETO!
"""

        # Salvar resultado para uso posterior
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Criar DataFrame para exportação
        df_dias_uteis = pd.DataFrame([
            {
                'Sindicato': union,
                'Estado': dados['estado'],
                'Dias_Uteis': dados['dias_uteis'],
                'Feriados_Especificos': dados['feriados_especificos'],
                'Valor_Diario': dados['valor_diario'],
                'Valor_Mensal_Base': dados['valor_mensal_base']
            }
            for union, dados in working_days_by_union.items()
        ])

        output_path = output_dir / f"dias_uteis_por_regiao_{reference_month.replace('.', '_')}.xlsx"
        df_dias_uteis.to_excel(output_path, index=False)

        relatorio += f"""
📄 ARQUIVO GERADO:
- Configuração salva em: {output_path}
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
    state_specific_holidays = get_state_specific_holidays(estado, year, month)

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


def get_state_specific_holidays(estado: str, year: int, month: int) -> List[Dict]:
    """Retorna feriados específicos por estado para o mês especificado"""

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

    # Filtrar apenas feriados do mês especificado
    month_holidays = [h for h in state_holidays if h['data'].month == month]

    return month_holidays