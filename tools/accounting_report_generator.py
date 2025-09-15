#!/usr/bin/env python3
"""
Gerador de Relatório Contábil - FinaCrew
Gera relatório detalhado em TXT com custos de VR/VA por cargo e funcionário
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

class AccountingReportGenerator:
    def __init__(self, output_dir="output", raw_data_dir="raw_data"):
        self.output_dir = Path(output_dir)
        self.raw_data_dir = Path(raw_data_dir)
        self.logger = logging.getLogger(__name__)
        
    def load_employee_data(self):
        """Carregar dados dos funcionários de todos os arquivos"""
        employee_data = []
        
        try:
            # Primeiro tentar carregar base consolidada
            consolidada_path = self.output_dir / "base_consolidada.xlsx"
            if consolidada_path.exists():
                try:
                    df = pd.read_excel(consolidada_path, sheet_name='Base Consolidada')
                    if not df.empty:
                        return df
                except:
                    pass
            
            # Se não encontrou base consolidada, procurar arquivos de funcionários
            for file_path in self.raw_data_dir.glob("*.xlsx"):
                if any(keyword in file_path.name.upper() for keyword in 
                      ['ATIVO', 'FUNCIONARIO', 'COLABORADOR', 'EMPLOYEE']):
                    
                    df = pd.read_excel(file_path)
                    
                    # Tentar identificar colunas importantes
                    cols_mapping = self._identify_columns(df)
                    
                    if cols_mapping['nome'] and cols_mapping['cargo']:
                        # Renomear colunas para padrão
                        df_clean = df.rename(columns=cols_mapping)
                        df_clean['arquivo_origem'] = file_path.name
                        employee_data.append(df_clean)
                        
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados de funcionários: {e}")
            
        if employee_data:
            return pd.concat(employee_data, ignore_index=True)
        return pd.DataFrame()
    
    def _identify_columns(self, df):
        """Identificar automaticamente as colunas importantes"""
        cols = {col.lower(): col for col in df.columns}
        mapping = {
            'nome': None,
            'cargo': None,
            'salario': None,
            'departamento': None,
            'data_admissao': None,
            'cpf': None
        }
        
        # Mapear nomes
        if 'nome' in cols:
            mapping['nome'] = cols['nome']
        elif 'funcionario' in cols:
            mapping['nome'] = cols['funcionario']
        elif 'colaborador' in cols:
            mapping['nome'] = cols['colaborador']
            
        # Mapear cargos
        if 'cargo' in cols:
            mapping['cargo'] = cols['cargo']
        elif 'funcao' in cols:
            mapping['cargo'] = cols['funcao']
        elif 'posicao' in cols:
            mapping['cargo'] = cols['posicao']
            
        # Mapear salário
        if 'salario' in cols:
            mapping['salario'] = cols['salario']
        elif 'remuneracao' in cols:
            mapping['salario'] = cols['remuneracao']
            
        # Mapear departamento
        if 'departamento' in cols:
            mapping['departamento'] = cols['departamento']
        elif 'setor' in cols:
            mapping['departamento'] = cols['setor']
            
        # Mapear data admissão
        if 'admissao' in cols:
            mapping['data_admissao'] = cols['admissao']
        elif 'data_admissao' in cols:
            mapping['data_admissao'] = cols['data_admissao']
            
        # Mapear CPF
        if 'cpf' in cols:
            mapping['cpf'] = cols['cpf']
            
        return mapping
    
    def calculate_vr_costs(self, employee_df):
        """Calcular custos de VR por cargo"""
        if employee_df.empty:
            return {}
            
        # Valores padrão VR (podem ser configuráveis)
        VALOR_VR_DIARIO = 28.00  # Valor médio diário VR
        DIAS_UTEIS_MES = 22      # Dias úteis por mês
        PERCENTUAL_EMPRESA = 0.80  # 80% empresa
        PERCENTUAL_FUNCIONARIO = 0.20  # 20% funcionário
        
        valor_mensal_por_funcionario = VALOR_VR_DIARIO * DIAS_UTEIS_MES
        custo_empresa_por_funcionario = valor_mensal_por_funcionario * PERCENTUAL_EMPRESA
        contribuicao_funcionario = valor_mensal_por_funcionario * PERCENTUAL_FUNCIONARIO
        
        # Agrupar por cargo
        cargo_stats = employee_df.groupby('cargo').agg({
            'nome': 'count',
            'salario': ['mean', 'sum'] if 'salario' in employee_df.columns else 'count'
        }).round(2)
        
        cargo_costs = {}
        for cargo in cargo_stats.index:
            qtd_funcionarios = cargo_stats.loc[cargo, ('nome', 'count')]
            
            cargo_costs[cargo] = {
                'quantidade': int(qtd_funcionarios),
                'custo_empresa_total': custo_empresa_por_funcionario * qtd_funcionarios,
                'contribuicao_funcionarios_total': contribuicao_funcionario * qtd_funcionarios,
                'valor_total_vr': valor_mensal_por_funcionario * qtd_funcionarios,
                'custo_empresa_unitario': custo_empresa_por_funcionario,
                'contribuicao_funcionario_unitaria': contribuicao_funcionario
            }
            
        return cargo_costs
    
    def generate_report(self, mes_referencia=None):
        """Gerar relatório contábil completo"""
        if not mes_referencia:
            mes_referencia = datetime.now().strftime("%m/%Y")
            
        # Carregar dados dos funcionários
        employee_df = self.load_employee_data()
        
        if employee_df.empty:
            self.logger.info("Nenhum dado de funcionário encontrado - relatório contábil não será gerado")
            return None
            
        # Calcular custos de VR
        cargo_costs = self.calculate_vr_costs(employee_df)
        
        # Gerar relatório
        report_content = self._format_report(cargo_costs, mes_referencia, employee_df)
        
        # Salvar arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_contabil_vr_{timestamp}.txt"
        report_path = self.output_dir / filename
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"Relatório contábil gerado: {report_path}")
        return str(report_path)
    
    def _format_report(self, cargo_costs, mes_referencia, employee_df):
        """Formatar relatório em texto"""
        
        # Calcular totais gerais
        total_funcionarios = sum(cargo['quantidade'] for cargo in cargo_costs.values())
        total_custo_empresa = sum(cargo['custo_empresa_total'] for cargo in cargo_costs.values())
        total_contribuicao_funcionarios = sum(cargo['contribuicao_funcionarios_total'] for cargo in cargo_costs.values())
        total_valor_vr = sum(cargo['valor_total_vr'] for cargo in cargo_costs.values())
        
        report = f"""
{'='*80}
                    RELATÓRIO CONTÁBIL - VALE REFEIÇÃO/ALIMENTAÇÃO
                                FinaCrew System v2.0
{'='*80}

PERÍODO DE REFERÊNCIA: {mes_referencia}
DATA DE EMISSÃO: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}

{'='*80}
                              RESUMO EXECUTIVO
{'='*80}

TOTAL DE FUNCIONÁRIOS ELEGÍVEIS: {total_funcionarios:>6} funcionários
CUSTO TOTAL EMPRESA (80%):       R$ {total_custo_empresa:>12,.2f}
CONTRIBUIÇÃO FUNCIONÁRIOS (20%): R$ {total_contribuicao_funcionarios:>12,.2f}
VALOR TOTAL VR MENSAL:           R$ {total_valor_vr:>12,.2f}

{'='*80}
                         DETALHAMENTO POR CARGO/FUNÇÃO
{'='*80}

"""
        
        # Ordenar cargos por quantidade de funcionários (decrescente)
        sorted_cargos = sorted(cargo_costs.items(), 
                              key=lambda x: x[1]['quantidade'], 
                              reverse=True)
        
        for i, (cargo, dados) in enumerate(sorted_cargos, 1):
            report += f"""
{i:2d}. CARGO: {cargo.upper()}
    {'-'*60}
    Quantidade de Funcionários:      {dados['quantidade']:>6} pessoas
    Custo Empresa (Mensal):         R$ {dados['custo_empresa_total']:>10,.2f}
    Contribuição Funcionários:      R$ {dados['contribuicao_funcionarios_total']:>10,.2f}
    Valor Total VR (Cargo):         R$ {dados['valor_total_vr']:>10,.2f}
    
    Valores Unitários (por funcionário):
    → Custo Empresa:                R$ {dados['custo_empresa_unitario']:>10,.2f}
    → Contribuição Funcionário:     R$ {dados['contribuicao_funcionario_unitaria']:>10,.2f}
    → Valor VR Total:               R$ {dados['custo_empresa_unitario'] + dados['contribuicao_funcionario_unitaria']:>10,.2f}

"""
        
        # Distribuição percentual
        report += f"""
{'='*80}
                           ANÁLISE PERCENTUAL POR CARGO
{'='*80}

"""
        
        for cargo, dados in sorted_cargos:
            percentual = (dados['quantidade'] / total_funcionarios) * 100
            report += f"• {cargo:<30} {dados['quantidade']:>4} func. ({percentual:>5.1f}%)\n"
        
        # Detalhes técnicos
        report += f"""

{'='*80}
                              DETALHES TÉCNICOS
{'='*80}

PARÂMETROS DE CÁLCULO:
• Valor VR Diário:               R$ 28,00
• Dias Úteis Considerados:       22 dias/mês
• Percentual Empresa:            80%
• Percentual Funcionário:        20%
• Valor VR Mensal/Funcionário:   R$ 616,00

COMPOSIÇÃO DO CUSTO MENSAL:
• Empresa (80%):                 R$ 492,80 por funcionário
• Funcionário (20%):             R$ 123,20 por funcionário

TOTAL DE ARQUIVOS PROCESSADOS:   {len(employee_df['arquivo_origem'].unique()) if 'arquivo_origem' in employee_df.columns else 'N/A'}

{'='*80}
                              INFORMAÇÕES CONTÁBEIS
{'='*80}

DÉBITO:
Conta: Despesas com Benefícios - Vale Refeição
Valor: R$ {total_custo_empresa:,.2f}

CRÉDITO:
Conta: Contas a Pagar - Fornecedor VR
Valor: R$ {total_valor_vr:,.2f}

Conta: Contas a Receber - Funcionários  
Valor: R$ {total_contribuicao_funcionarios:,.2f}

LANÇAMENTO CONTÁBIL SUGERIDO:
D - Despesas com Vale Refeição      R$ {total_custo_empresa:,.2f}
D - Adiantamentos a Funcionários    R$ {total_contribuicao_funcionarios:,.2f}
C - Fornecedores - Vale Refeição    R$ {total_valor_vr:,.2f}

{'='*80}
                                 OBSERVAÇÕES
{'='*80}

1. Os valores apresentados referem-se ao mês de {mes_referencia}
2. Cálculos baseados em 22 dias úteis por mês
3. Percentuais: 80% Empresa / 20% Funcionário (padrão CLT)
4. Valores sujeitos a alterações conforme acordo coletivo
5. Relatório gerado automaticamente pelo sistema FinaCrew

{'='*80}
                           FIM DO RELATÓRIO CONTÁBIL
{'='*80}

Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
Sistema: FinaCrew v2.0 - Processamento Inteligente de Benefícios
"""
        
        return report