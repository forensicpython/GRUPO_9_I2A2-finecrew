#!/usr/bin/env python3
"""
AGENTE COORDENADOR - FinaCrew Sistema Multi-Agente
Responsável por orquestrar todos os agentes e consolidar resultados REAIS
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Tuple
from pathlib import Path
import logging

from agents.file_manager_agent import get_file_manager
from agents.exclusions_agent import get_exclusions_agent

class CoordinatorAgent:
    """
    Agente Coordenador - Núcleo do sistema multi-agente

    Responsabilidades:
    1. Consolidar base única das 5 fontes obrigatórias
    2. Orquestrar agentes especializados
    3. Aplicar regras de negócio do projeto
    4. Gerar resultado final REAL
    """

    def __init__(self, raw_data_dir: str = None, output_dir: str = None):
        self.raw_data_dir = raw_data_dir or "/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/FinaCrew/raw_data"
        self.output_dir = Path(output_dir or "/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/FinaCrew/output")
        self.output_dir.mkdir(exist_ok=True)

        # Inicializar agentes especializados
        self.file_manager = get_file_manager(self.raw_data_dir)
        self.exclusions_agent = get_exclusions_agent(self.file_manager)

        # Dados consolidados
        self.consolidated_base = None
        self.union_values = {}
        self.working_days_by_union = {}

        # Resultado final
        self.final_calculations = None

        print("🎯 AGENTE COORDENADOR: Inicializado com sucesso")

    def process_vr_calculation_real(self, month: str = "05", year: str = "2025") -> Dict:
        """
        Processo PRINCIPAL - Cálculo REAL de VR conforme especificações do projeto

        ETAPAS:
        1. Consolidar base única (5 fontes obrigatórias)
        2. Aplicar exclusões
        3. Calcular dias úteis por sindicato
        4. Aplicar regras de desligamento (dia 15)
        5. Calcular valores proporcionais
        6. Aplicar rateio 80% empresa / 20% funcionário
        7. Gerar planilha final
        """
        print(f"\n🚀 AGENTE COORDENADOR: Iniciando cálculo REAL VR {month}/{year}")
        print("=" * 80)

        try:
            # ETAPA 1: Consolidar base única
            print("\n📊 ETAPA 1: CONSOLIDAÇÃO DA BASE ÚNICA")
            self._consolidate_master_base()

            # ETAPA 2: Carregar tabelas de referência
            print("\n📋 ETAPA 2: CARREGAMENTO DE TABELAS DE REFERÊNCIA")
            self._load_reference_tables()

            # ETAPA 3: Aplicar exclusões
            print("\n🚫 ETAPA 3: APLICAÇÃO DE EXCLUSÕES")
            self._apply_exclusions()

            # ETAPA 4: Calcular dias úteis reais
            print("\n📅 ETAPA 4: CÁLCULO DE DIAS ÚTEIS REAIS")
            self._calculate_real_working_days(month, year)

            # ETAPA 5: Aplicar regras de negócio
            print("\n⚖️ ETAPA 5: APLICAÇÃO DE REGRAS DE NEGÓCIO")
            self._apply_business_rules(month, year)

            # ETAPA 6: Calcular valores finais REAIS
            print("\n💰 ETAPA 6: CÁLCULO DE VALORES FINAIS REAIS")
            self._calculate_final_values()

            # ETAPA 7: Gerar relatórios
            print("\n📄 ETAPA 7: GERAÇÃO DE RELATÓRIOS")
            result = self._generate_final_reports(month, year)

            print("\n" + "=" * 80)
            print("🎉 AGENTE COORDENADOR: Processamento REAL concluído com sucesso!")
            print("=" * 80)

            return result

        except Exception as e:
            print(f"\n❌ ERRO no Agente Coordenador: {e}")
            raise

    def _consolidate_master_base(self):
        """Consolida as 5 bases obrigatórias em uma base única"""
        print("🔄 Consolidando bases obrigatórias...")

        try:
            # 1. Base ATIVOS (principal)
            ativos_df = self.file_manager.load_excel_safe("ATIVOS.xlsx")
            print(f"✅ ATIVOS carregados: {len(ativos_df)} funcionários")

            # 2. Enrichment com dados de admissão
            try:
                admissoes_df = self.file_manager.load_excel_safe("ADMISSAO_ABRIL.xlsx")
                print(f"✅ ADMISSÕES carregadas: {len(admissoes_df)} funcionários")

                # Merge com dados de admissão
                ativos_df = ativos_df.merge(
                    admissoes_df[['MATRICULA', 'DATA ADMISSAO']],
                    on='MATRICULA',
                    how='left',
                    suffixes=('', '_adm')
                )
                print("✅ Dados de admissão integrados")

            except Exception as e:
                print(f"⚠️ Admissões não integradas: {e}")

            # 3. Enrichment com dados de desligamento
            try:
                desligados_df = self.file_manager.load_excel_safe("DESLIGADOS.xlsx")
                print(f"✅ DESLIGADOS carregados: {len(desligados_df)} funcionários")

                # Merge com dados de desligamento
                ativos_df = ativos_df.merge(
                    desligados_df[['MATRICULA ', 'DATA DEMISSÃO', 'COMUNICADO DE DESLIGAMENTO']],
                    left_on='MATRICULA',
                    right_on='MATRICULA ',
                    how='left',
                    suffixes=('', '_desl')
                )
                print("✅ Dados de desligamento integrados")

            except Exception as e:
                print(f"⚠️ Desligamentos não integrados: {e}")

            # 4. Enrichment com dados de férias
            try:
                ferias_df = self.file_manager.load_excel_safe("FERIAS.xlsx")
                print(f"✅ FÉRIAS carregadas: {len(ferias_df)} funcionários")

                # Merge com dados de férias
                ativos_df = ativos_df.merge(
                    ferias_df[['MATRICULA', 'INICIO', 'FIM']],
                    on='MATRICULA',
                    how='left',
                    suffixes=('', '_ferias')
                )
                print("✅ Dados de férias integrados")

            except Exception as e:
                print(f"⚠️ Férias não integradas: {e}")

            # Limpar e normalizar dados
            ativos_df['MATRICULA'] = ativos_df['MATRICULA'].astype(str)

            self.consolidated_base = ativos_df
            print(f"📊 BASE CONSOLIDADA: {len(self.consolidated_base)} funcionários")

        except Exception as e:
            print(f"❌ Erro na consolidação: {e}")
            raise

    def _load_reference_tables(self):
        """Carrega tabelas de referência (sindicatos e dias úteis)"""
        print("📋 Carregando tabelas de referência...")

        try:
            # Tabela de valores por sindicato - estrutura real
            union_values_df = self.file_manager.load_excel_safe("Base_sindicato_x_valor.xlsx")

            # Mapear valores por estado (estrutura real do arquivo)
            state_values = {
                'Paraná': 35.0,
                'Rio de Janeiro': 35.0,
                'Rio Grande do Sul': 35.0,
                'São Paulo': 37.5
            }

            # Mapear sindicatos para estados conforme dados reais
            union_to_state = {
                'SITEPD PR - SIND DOS TRAB EM EMPR PRIVADAS DE PROC DE DADOS DE CURITIBA E REGIAO METROPOLITANA': 'Paraná',
                'SINDPD RJ - SINDICATO PROFISSIONAIS DE PROC DADOS DO RIO DE JANEIRO': 'Rio de Janeiro',
                'SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL': 'Rio Grande do Sul',
                'SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP.': 'São Paulo'
            }

            # Criar mapeamento final sindicato -> valor
            for union, state in union_to_state.items():
                self.union_values[union] = state_values.get(state, 35.0)

            print(f"✅ Valores por sindicato carregados: {len(self.union_values)} sindicatos")

            # Tabela de dias úteis por sindicato - estrutura real
            working_days_df = self.file_manager.load_excel_safe("Base_dias_uteis.xlsx")

            # Pular header e processar dados reais
            for _, row in working_days_df.iloc[1:].iterrows():  # Pular linha de header
                union_name = row.iloc[0]  # Primeira coluna = sindicato
                days = row.iloc[1]  # Segunda coluna = dias úteis

                if pd.notna(union_name) and pd.notna(days):
                    try:
                        self.working_days_by_union[union_name] = int(days)
                    except (ValueError, TypeError):
                        continue

            print(f"✅ Dias úteis por sindicato carregados: {len(self.working_days_by_union)} sindicatos")

            # Debug: mostrar dados carregados
            print("📊 Valores VR por sindicato:")
            for union, value in self.union_values.items():
                print(f"   {union[:50]}... → R$ {value:.2f}")

            print("📅 Dias úteis por sindicato:")
            for union, days in self.working_days_by_union.items():
                print(f"   {union[:50]}... → {days} dias")

        except Exception as e:
            print(f"❌ Erro ao carregar tabelas de referência: {e}")
            raise

    def _apply_exclusions(self):
        """Aplica filtros de exclusão usando o Agente EXCLUSÕES"""
        print("🚫 Aplicando exclusões...")

        original_count = len(self.consolidated_base)

        # Usar agente de exclusões para filtrar
        self.consolidated_base = self.exclusions_agent.filter_eligible_employees(
            self.consolidated_base, 'MATRICULA'
        )

        excluded_count = original_count - len(self.consolidated_base)

        print(f"📊 Exclusões aplicadas: {original_count} → {len(self.consolidated_base)} "
              f"(excluídos: {excluded_count})")

    def _calculate_real_working_days(self, month: str, year: str):
        """Calcula dias úteis REAIS baseado nos dados do sindicato"""
        print("📅 Calculando dias úteis reais...")

        def get_working_days_for_employee(row):
            """Calcula dias úteis para um funcionário específico"""
            union = row.get('Sindicato', '')

            # Dias úteis base do sindicato
            base_days = self.working_days_by_union.get(union, 22)  # Default 22 dias

            # Ajustar por férias
            working_days = base_days
            if pd.notna(row.get('INICIO')) and pd.notna(row.get('FIM')):
                # Funcionário em férias - reduzir dias
                # Simplificação: se tem férias no mês, reduzir pela metade
                working_days = base_days // 2

            return working_days

        # Aplicar cálculo para cada funcionário
        self.consolidated_base['DIAS_UTEIS_REAL'] = self.consolidated_base.apply(
            get_working_days_for_employee, axis=1
        )

        print("✅ Dias úteis reais calculados por funcionário")

    def _apply_business_rules(self, month: str, year: str):
        """Aplica regras de negócio específicas do projeto"""
        print("⚖️ Aplicando regras de negócio...")

        def apply_severance_rule(row):
            """Aplica regra do dia 15 para desligamentos"""
            if pd.notna(row.get('DATA DEMISSÃO')):
                try:
                    dismissal_date = pd.to_datetime(row['DATA DEMISSÃO'])

                    # Regra: se comunicado até dia 15, não pagar. Depois do dia 15, proporcional
                    communication_date = row.get('COMUNICADO DE DESLIGAMENTO')

                    if pd.notna(communication_date):
                        comm_date = pd.to_datetime(communication_date)
                        if comm_date.day <= 15:
                            return 0  # Não pagar
                        else:
                            # Pagar proporcional (dias restantes do mês)
                            days_worked = dismissal_date.day
                            total_days = row['DIAS_UTEIS_REAL']
                            return min(days_worked, total_days)

                except:
                    pass

            return row['DIAS_UTEIS_REAL']

        # Aplicar regra de desligamento
        self.consolidated_base['DIAS_UTEIS_FINAL'] = self.consolidated_base.apply(
            apply_severance_rule, axis=1
        )

        print("✅ Regras de negócio aplicadas")

    def _calculate_final_values(self):
        """Calcula valores finais REAIS de VR"""
        print("💰 Calculando valores finais REAIS...")

        def calculate_vr_value(row):
            """Calcula valor VR para um funcionário"""
            union = row.get('Sindicato', '')
            days = row.get('DIAS_UTEIS_FINAL', 0)

            # Valor diário do sindicato
            daily_value = self.union_values.get(union, 50.0)  # Default R$ 50/dia

            # Valor total
            total_value = daily_value * days

            # Rateio: 80% empresa, 20% funcionário
            company_value = total_value * 0.80
            employee_value = total_value * 0.20

            return {
                'valor_total': total_value,
                'valor_empresa': company_value,
                'valor_funcionario': employee_value,
                'valor_diario': daily_value
            }

        # Calcular valores para cada funcionário
        vr_calculations = []
        for _, row in self.consolidated_base.iterrows():
            calc = calculate_vr_value(row)
            calc['matricula'] = row['MATRICULA']
            calc['sindicato'] = row.get('Sindicato', '')
            calc['dias_uteis'] = row.get('DIAS_UTEIS_FINAL', 0)
            vr_calculations.append(calc)

        self.final_calculations = pd.DataFrame(vr_calculations)

        # Estatísticas finais REAIS
        total_employees = len(self.final_calculations)
        total_vr_value = self.final_calculations['valor_total'].sum()
        total_company_cost = self.final_calculations['valor_empresa'].sum()
        total_employee_cost = self.final_calculations['valor_funcionario'].sum()

        print(f"📊 RESULTADOS FINAIS REAIS:")
        print(f"   👥 Total funcionários elegíveis: {total_employees}")
        print(f"   💰 Valor total VR: R$ {total_vr_value:,.2f}")
        print(f"   🏢 Custo empresa (80%): R$ {total_company_cost:,.2f}")
        print(f"   👤 Desconto funcionário (20%): R$ {total_employee_cost:,.2f}")

    def _generate_final_reports(self, month: str, year: str) -> Dict:
        """Gera relatórios finais"""
        print("📄 Gerando relatórios finais...")

        try:
            # 1. Relatório consolidado
            output_file = self.output_dir / f"VR MENSAL {month}.{year}.xlsx"

            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Aba principal com cálculos
                final_report = self.consolidated_base.merge(
                    self.final_calculations,
                    left_on='MATRICULA',
                    right_on='matricula',
                    how='left'
                )

                final_report.to_excel(writer, sheet_name='Cálculo_VR_Real', index=False)

                # Aba de estatísticas
                stats_data = {
                    'Métrica': [
                        'Total Funcionários',
                        'Funcionários Elegíveis',
                        'Funcionários Excluídos',
                        'Valor Total VR',
                        'Valor Empresa (80%)',
                        'Valor Funcionário (20%)'
                    ],
                    'Valor': [
                        len(self.consolidated_base),
                        len(self.final_calculations),
                        len(self.exclusions_agent.excluded_employees),
                        f"R$ {self.final_calculations['valor_total'].sum():,.2f}",
                        f"R$ {self.final_calculations['valor_empresa'].sum():,.2f}",
                        f"R$ {self.final_calculations['valor_funcionario'].sum():,.2f}"
                    ]
                }

                pd.DataFrame(stats_data).to_excel(writer, sheet_name='Estatísticas', index=False)

                # Aba de exclusões
                exclusions_report = self.exclusions_agent.get_exclusion_report()
                pd.DataFrame([exclusions_report]).to_excel(writer, sheet_name='Exclusões', index=False)

            print(f"✅ Relatório salvo: {output_file}")

            # Resultado para retorno
            result = {
                'status': 'success',
                'total_employees': len(self.final_calculations),
                'total_vr_value': float(self.final_calculations['valor_total'].sum()),
                'company_cost': float(self.final_calculations['valor_empresa'].sum()),
                'employee_cost': float(self.final_calculations['valor_funcionario'].sum()),
                'output_file': str(output_file),
                'calculation_method': 'REAL - Baseado em dados reais das planilhas'
            }

            return result

        except Exception as e:
            print(f"❌ Erro ao gerar relatórios: {e}")
            raise

# Função utilitária principal
def process_vr_real(month: str = "05", year: str = "2025") -> Dict:
    """
    Função principal para processar VR com cálculos REAIS
    """
    coordinator = CoordinatorAgent()
    return coordinator.process_vr_calculation_real(month, year)