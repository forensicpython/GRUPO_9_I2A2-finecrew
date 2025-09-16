#!/usr/bin/env python3
"""
AGENTE EXCLUSÕES - FinaCrew Sistema Multi-Agente
Responsável por filtrar funcionários inelegíveis ao VR conforme regras do projeto
"""

import pandas as pd
from typing import Dict, List, Set
import re
from agents.file_manager_agent import get_file_manager

class ExclusionsAgent:
    """
    Agente responsável por identificar e excluir funcionários inelegíveis

    Regras de exclusão conforme projeto:
    - Diretores
    - Estagiários
    - Aprendizes
    - Afastados (licença maternidade, etc.)
    - Funcionários que atuam no exterior
    """

    def __init__(self, file_manager=None):
        self.file_manager = file_manager or get_file_manager()
        self.excluded_employees = set()
        self.exclusion_reasons = {}

    def identify_exclusions(self) -> Dict[str, Set[str]]:
        """
        Identifica funcionários que devem ser excluídos do cálculo de VR
        Retorna dict com categorias de exclusão e matrículas
        """
        print("🚫 Agente EXCLUSÕES: Identificando funcionários inelegíveis...")

        exclusions = {
            'diretores': set(),
            'estagiarios': set(),
            'aprendizes': set(),
            'afastados': set(),
            'exterior': set()
        }

        # 1. DIRETORES - Identificar por cargo
        print("🔍 Identificando DIRETORES...")
        try:
            ativos_df = self.file_manager.load_excel_safe("ATIVOS.xlsx")

            director_patterns = [
                r'diretor', r'diretora', r'ceo', r'presidente',
                r'vice.presidente', r'superintendente'
            ]

            for _, row in ativos_df.iterrows():
                cargo = str(row.get('TITULO DO CARGO', '')).lower()
                matricula = str(row.get('MATRICULA', ''))

                for pattern in director_patterns:
                    if re.search(pattern, cargo):
                        exclusions['diretores'].add(matricula)
                        self.exclusion_reasons[matricula] = f"Diretor: {cargo}"
                        break

            print(f"📊 DIRETORES identificados: {len(exclusions['diretores'])}")

        except Exception as e:
            print(f"❌ Erro ao identificar diretores: {e}")

        # 2. ESTAGIÁRIOS
        print("🔍 Identificando ESTAGIÁRIOS...")
        try:
            estagio_df = self.file_manager.load_excel_safe("ESTAGIO.xlsx")

            for _, row in estagio_df.iterrows():
                matricula = str(row.get('MATRICULA', ''))
                if matricula and matricula != 'nan':
                    exclusions['estagiarios'].add(matricula)
                    self.exclusion_reasons[matricula] = "Estagiário"

            print(f"📊 ESTAGIÁRIOS identificados: {len(exclusions['estagiarios'])}")

        except Exception as e:
            print(f"❌ Erro ao identificar estagiários: {e}")

        # 3. APRENDIZES
        print("🔍 Identificando APRENDIZES...")
        try:
            aprendiz_df = self.file_manager.load_excel_safe("APRENDIZ.xlsx")

            for _, row in aprendiz_df.iterrows():
                matricula = str(row.get('MATRICULA', ''))
                if matricula and matricula != 'nan':
                    exclusions['aprendizes'].add(matricula)
                    self.exclusion_reasons[matricula] = "Aprendiz"

            print(f"📊 APRENDIZES identificados: {len(exclusions['aprendizes'])}")

        except Exception as e:
            print(f"❌ Erro ao identificar aprendizes: {e}")

        # 4. AFASTADOS
        print("🔍 Identificando AFASTADOS...")
        try:
            afastamentos_df = self.file_manager.load_excel_safe("AFASTAMENTOS.xlsx")

            for _, row in afastamentos_df.iterrows():
                matricula = str(row.get('MATRICULA', ''))
                motivo = str(row.get('MOTIVO', ''))
                if matricula and matricula != 'nan':
                    exclusions['afastados'].add(matricula)
                    self.exclusion_reasons[matricula] = f"Afastado: {motivo}"

            print(f"📊 AFASTADOS identificados: {len(exclusions['afastados'])}")

        except Exception as e:
            print(f"❌ Erro ao identificar afastados: {e}")

        # 5. EXTERIOR
        print("🔍 Identificando funcionários no EXTERIOR...")
        try:
            exterior_df = self.file_manager.load_excel_safe("EXTERIOR.xlsx")

            for _, row in exterior_df.iterrows():
                matricula = str(row.get('MATRICULA', ''))
                if matricula and matricula != 'nan':
                    exclusions['exterior'].add(matricula)
                    self.exclusion_reasons[matricula] = "Trabalha no exterior"

            print(f"📊 EXTERIOR identificados: {len(exclusions['exterior'])}")

        except Exception as e:
            print(f"❌ Erro ao identificar funcionários no exterior: {e}")

        # Consolidar todas as exclusões
        all_excluded = set()
        for category, matriculas in exclusions.items():
            all_excluded.update(matriculas)

        self.excluded_employees = all_excluded

        print(f"🚫 TOTAL DE EXCLUSÕES: {len(all_excluded)} funcionários")
        self._print_exclusion_summary(exclusions)

        return exclusions

    def is_employee_excluded(self, matricula: str) -> bool:
        """Verifica se um funcionário específico deve ser excluído"""
        return str(matricula) in self.excluded_employees

    def get_exclusion_reason(self, matricula: str) -> str:
        """Retorna motivo da exclusão para uma matrícula"""
        return self.exclusion_reasons.get(str(matricula), "Não excluído")

    def filter_eligible_employees(self, df: pd.DataFrame, matricula_column: str = 'MATRICULA') -> pd.DataFrame:
        """
        Filtra DataFrame removendo funcionários excluídos
        """
        if df.empty:
            return df

        original_count = len(df)

        # Converter matrícula para string para comparação
        df_copy = df.copy()
        df_copy[matricula_column] = df_copy[matricula_column].astype(str)

        # Filtrar funcionários elegíveis
        eligible_df = df_copy[~df_copy[matricula_column].isin(self.excluded_employees)]

        excluded_count = original_count - len(eligible_df)

        print(f"📊 Filtro de Exclusões: {original_count} → {len(eligible_df)} "
              f"(excluídos: {excluded_count})")

        return eligible_df

    def get_exclusion_report(self) -> Dict:
        """Gera relatório detalhado das exclusões"""
        exclusions = self.identify_exclusions()

        report = {
            'total_excluded': len(self.excluded_employees),
            'by_category': {k: len(v) for k, v in exclusions.items()},
            'detailed_reasons': self.exclusion_reasons,
            'excluded_matriculas': list(self.excluded_employees)
        }

        return report

    def _print_exclusion_summary(self, exclusions: Dict[str, Set[str]]):
        """Imprime resumo das exclusões"""
        print("\n📋 RESUMO DAS EXCLUSÕES:")
        print("=" * 40)

        for category, matriculas in exclusions.items():
            if matriculas:
                print(f"🚫 {category.upper()}: {len(matriculas)} funcionários")

        print("=" * 40)

    def save_exclusions_report(self, output_path: str):
        """Salva relatório de exclusões em Excel"""
        try:
            exclusions = self.identify_exclusions()

            # Criar DataFrame do relatório
            exclusion_data = []
            for matricula in self.excluded_employees:
                reason = self.exclusion_reasons.get(matricula, "Motivo não especificado")
                exclusion_data.append({
                    'MATRICULA': matricula,
                    'MOTIVO_EXCLUSAO': reason
                })

            exclusions_df = pd.DataFrame(exclusion_data)

            # Salvar em Excel com múltiplas abas
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                exclusions_df.to_excel(writer, sheet_name='Exclusões_Geral', index=False)

                # Aba por categoria
                for category, matriculas in exclusions.items():
                    if matriculas:
                        category_data = []
                        for matricula in matriculas:
                            reason = self.exclusion_reasons.get(matricula, category)
                            category_data.append({
                                'MATRICULA': matricula,
                                'MOTIVO': reason
                            })

                        category_df = pd.DataFrame(category_data)
                        sheet_name = category.capitalize()[:31]  # Limite do Excel
                        category_df.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"💾 Relatório de exclusões salvo: {output_path}")

        except Exception as e:
            print(f"❌ Erro ao salvar relatório de exclusões: {e}")

# Função utilitária
def get_exclusions_agent(file_manager=None) -> ExclusionsAgent:
    """Retorna instância configurada do Exclusions Agent"""
    agent = ExclusionsAgent(file_manager)
    agent.identify_exclusions()  # Inicializar exclusões
    return agent