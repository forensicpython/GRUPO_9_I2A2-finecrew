#!/usr/bin/env python3
"""
Analisador Automático de Planilhas de Funcionários
Identifica automaticamente se uma planilha contém dados de funcionários
e classifica o tipo de lista (ATIVOS, FÉRIAS, DESLIGADOS, etc.)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpreadsheetAnalyzer:
    """Analisador automático de planilhas de funcionários"""
    
    def __init__(self):
        # Padrões de campos comuns em planilhas de funcionários
        self.employee_field_patterns = {
            'matricula': [
                'matricula', 'matrícula', 'mat', 'codigo', 'código', 
                'id', 'registro', 'chapa', 'número', 'numero'
            ],
            'nome': [
                'nome', 'funcionario', 'funcionário', 'colaborador', 
                'empregado', 'pessoa', 'trabalhador'
            ],
            'cpf': [
                'cpf', 'documento', 'doc', 'identificacao', 'identificação'
            ],
            'cargo': [
                'cargo', 'função', 'funcao', 'posicao', 'posição', 
                'ocupacao', 'ocupação', 'atividade'
            ],
            'departamento': [
                'departamento', 'setor', 'area', 'área', 'divisao', 
                'divisão', 'unidade', 'centro'
            ],
            'data_admissao': [
                'admissao', 'admissão', 'entrada', 'inicio', 'início', 
                'contratacao', 'contratação', 'data_admissao'
            ],
            'data_demissao': [
                'demissao', 'demissão', 'saida', 'saída', 'desligamento', 
                'rescisao', 'rescisão', 'data_demissao'
            ],
            'salario': [
                'salario', 'salário', 'remuneracao', 'remuneração', 
                'valor', 'vencimento', 'pagamento'
            ],
            'ferias': [
                'ferias', 'férias', 'gozo', 'periodo', 'período'
            ]
        }
        
        # Padrões para classificar tipos de planilha
        self.sheet_type_indicators = {
            'ATIVOS': {
                'required_fields': ['matricula', 'nome'],
                'forbidden_fields': ['data_demissao'],
                'keywords': ['ativo', 'ativos', 'funcionarios', 'colaboradores']
            },
            'DESLIGADOS': {
                'required_fields': ['matricula', 'nome', 'data_demissao'],
                'forbidden_fields': [],
                'keywords': ['desligado', 'demitido', 'rescisao', 'saida']
            },
            'FERIAS': {
                'required_fields': ['matricula', 'nome'],
                'forbidden_fields': [],
                'keywords': ['ferias', 'gozo', 'periodo']
            },
            'ADMISSAO': {
                'required_fields': ['matricula', 'nome', 'data_admissao'],
                'forbidden_fields': [],
                'keywords': ['admissao', 'contratacao', 'entrada', 'abril']
            },
            'SINDICATO': {
                'required_fields': ['sindicato', 'valor'],
                'forbidden_fields': [],
                'keywords': ['sindicato', 'categoria', 'base', 'valor']
            }
        }

    def normalize_text(self, text: str) -> str:
        """Normalizar texto para comparação"""
        if pd.isna(text):
            return ""
        
        text = str(text).lower().strip()
        # Remover acentos
        replacements = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
            'é': 'e', 'ê': 'e', 'è': 'e',
            'í': 'i', 'î': 'i', 'ì': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o', 'ò': 'o',
            'ú': 'u', 'û': 'u', 'ù': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remover caracteres especiais
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.strip()

    def detect_field_type(self, column_name: str, sample_data: pd.Series) -> Optional[str]:
        """Detectar o tipo de campo baseado no nome da coluna e dados"""
        normalized_name = self.normalize_text(column_name)
        
        # Verificar padrões de nome
        for field_type, patterns in self.employee_field_patterns.items():
            for pattern in patterns:
                if pattern in normalized_name:
                    return field_type
        
        # Análise dos dados para confirmar tipo
        if not sample_data.empty:
            # Verificar se parece com matrícula (números sequenciais)
            if sample_data.dtype in ['int64', 'float64'] or all(str(x).isdigit() for x in sample_data.dropna().head()):
                if 'mat' in normalized_name or 'cod' in normalized_name or 'id' in normalized_name:
                    return 'matricula'
            
            # Verificar se parece com CPF
            if sample_data.dtype == 'object':
                cpf_pattern = re.compile(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}')
                if any(cpf_pattern.match(str(x)) for x in sample_data.dropna().head()):
                    return 'cpf'
            
            # Verificar se parece com data
            try:
                # Suprimir warning de formato de data
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    pd.to_datetime(sample_data.dropna().head(), errors='coerce')
                if any(word in normalized_name for word in ['data', 'admissao', 'demissao', 'inicio', 'saida']):
                    if any(word in normalized_name for word in ['admissao', 'entrada', 'contrato']):
                        return 'data_admissao'
                    elif any(word in normalized_name for word in ['demissao', 'saida', 'rescisao']):
                        return 'data_demissao'
            except:
                pass
        
        return None

    def analyze_spreadsheet(self, file_path: str) -> Dict:
        """Analisar uma planilha e determinar se contém dados de funcionários"""
        try:
            logger.info(f"🔍 Analisando planilha: {file_path}")
            
            # Ler a planilha
            df = pd.read_excel(file_path)
            
            if df.empty:
                return {
                    'is_employee_list': False,
                    'confidence': 0,
                    'sheet_type': 'UNKNOWN',
                    'error': 'Planilha vazia'
                }
            
            # Analisar colunas
            detected_fields = {}
            field_confidence = {}
            
            for column in df.columns:
                sample_data = df[column].dropna().head(10)
                field_type = self.detect_field_type(column, sample_data)
                
                if field_type:
                    detected_fields[field_type] = column
                    # Calcular confiança baseada na qualidade dos dados
                    field_confidence[field_type] = self.calculate_field_confidence(field_type, sample_data)
            
            # Determinar se é lista de funcionários
            is_employee_list = self.is_employee_spreadsheet(detected_fields, df)
            
            # Classificar tipo de planilha
            sheet_type, type_confidence = self.classify_sheet_type(detected_fields, df, file_path)
            
            # Calcular confiança geral
            overall_confidence = self.calculate_overall_confidence(
                is_employee_list, detected_fields, field_confidence, type_confidence
            )
            
            # Análise estatística dos dados
            statistics = self.generate_statistics(df, detected_fields)
            
            result = {
                'is_employee_list': is_employee_list,
                'confidence': overall_confidence,
                'sheet_type': sheet_type,
                'detected_fields': detected_fields,
                'field_confidence': field_confidence,
                'statistics': statistics,
                'recommendations': self.generate_recommendations(detected_fields, sheet_type),
                'file_name': Path(file_path).name,
                'total_rows': len(df),
                'total_columns': len(df.columns)
            }
            
            logger.info(f"✅ Análise concluída: {sheet_type} (confiança: {overall_confidence:.1%})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar planilha {file_path}: {str(e)}")
            return {
                'is_employee_list': False,
                'confidence': 0,
                'sheet_type': 'ERROR',
                'error': str(e)
            }

    def calculate_field_confidence(self, field_type: str, sample_data: pd.Series) -> float:
        """Calcular confiança de um campo específico"""
        if sample_data.empty:
            return 0.0
        
        # Verificações específicas por tipo de campo
        if field_type == 'matricula':
            # Verificar se são números únicos e sequenciais
            try:
                numeric_data = pd.to_numeric(sample_data, errors='coerce').dropna()
                if len(numeric_data) > 0:
                    uniqueness = len(numeric_data.unique()) / len(numeric_data)
                    return min(1.0, uniqueness * 1.2)
            except:
                pass
            return 0.5
        
        elif field_type == 'nome':
            # Verificar se contém nomes válidos (múltiplas palavras, caracteres alfabéticos)
            valid_names = 0
            for name in sample_data:
                if isinstance(name, str) and len(name.split()) >= 2 and any(c.isalpha() for c in name):
                    valid_names += 1
            return valid_names / len(sample_data) if len(sample_data) > 0 else 0
        
        elif field_type == 'cpf':
            # Verificar formato de CPF
            valid_cpfs = 0
            for cpf in sample_data:
                if isinstance(cpf, str) and re.match(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', cpf):
                    valid_cpfs += 1
            return valid_cpfs / len(sample_data) if len(sample_data) > 0 else 0
        
        elif field_type in ['data_admissao', 'data_demissao']:
            # Verificar se são datas válidas
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    valid_dates = pd.to_datetime(sample_data, errors='coerce').notna().sum()
                return valid_dates / len(sample_data) if len(sample_data) > 0 else 0
            except:
                return 0
        
        return 0.7  # Confiança padrão para outros campos

    def is_employee_spreadsheet(self, detected_fields: Dict, df: pd.DataFrame) -> bool:
        """Determinar se a planilha contém dados de funcionários"""
        # Verificar campos essenciais
        essential_fields = ['matricula', 'nome']
        has_essential = any(field in detected_fields for field in essential_fields)
        
        # Verificar tamanho mínimo da planilha
        has_minimum_size = len(df) >= 5 and len(df.columns) >= 2
        
        # Verificar se não é planilha de configuração
        is_not_config = len(df) > 10  # Planilhas de config geralmente são pequenas
        
        return has_essential and has_minimum_size and is_not_config

    def classify_sheet_type(self, detected_fields: Dict, df: pd.DataFrame, file_path: str) -> Tuple[str, float]:
        """Classificar o tipo de planilha"""
        file_name = self.normalize_text(Path(file_path).name)
        
        best_match = 'UNKNOWN'
        best_confidence = 0.0
        
        for sheet_type, indicators in self.sheet_type_indicators.items():
            confidence = 0.0
            
            # Verificar campos obrigatórios
            required_score = 0
            for required_field in indicators['required_fields']:
                if required_field in detected_fields:
                    required_score += 1
            
            if len(indicators['required_fields']) > 0:
                confidence += (required_score / len(indicators['required_fields'])) * 0.4
            
            # Verificar campos proibidos
            forbidden_penalty = 0
            for forbidden_field in indicators['forbidden_fields']:
                if forbidden_field in detected_fields:
                    forbidden_penalty += 0.2
            confidence -= forbidden_penalty
            
            # Verificar palavras-chave no nome do arquivo
            keyword_score = 0
            for keyword in indicators['keywords']:
                if keyword in file_name:
                    keyword_score += 1
            
            if len(indicators['keywords']) > 0:
                confidence += (keyword_score / len(indicators['keywords'])) * 0.6
            
            # Verificações específicas por tipo
            if sheet_type == 'SINDICATO':
                # Planilhas de sindicato são geralmente menores
                if len(df) < 100:
                    confidence += 0.2
                # Verificar se tem campos de valor/categoria
                if any('valor' in self.normalize_text(str(col)) for col in df.columns):
                    confidence += 0.3
            
            confidence = max(0.0, min(1.0, confidence))
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = sheet_type
        
        return best_match, best_confidence

    def calculate_overall_confidence(self, is_employee_list: bool, detected_fields: Dict, 
                                   field_confidence: Dict, type_confidence: float) -> float:
        """Calcular confiança geral da análise"""
        if not is_employee_list:
            return 0.0
        
        # Confiança média dos campos
        if field_confidence:
            avg_field_confidence = sum(field_confidence.values()) / len(field_confidence)
        else:
            avg_field_confidence = 0.0
        
        # Peso dos campos detectados
        field_weight = min(1.0, len(detected_fields) / 4)  # Ideal: 4+ campos
        
        # Combinação das confiânças
        overall = (avg_field_confidence * 0.4 + type_confidence * 0.4 + field_weight * 0.2)
        
        return min(1.0, overall)

    def generate_statistics(self, df: pd.DataFrame, detected_fields: Dict) -> Dict:
        """Gerar estatísticas da planilha"""
        stats = {
            'total_rows': len(df),
            'non_empty_rows': df.dropna(how='all').shape[0],
            'completeness': {},
            'data_quality': {}
        }
        
        # Análise de completude por campo
        for field_type, column in detected_fields.items():
            if column in df.columns:
                non_null_count = df[column].notna().sum()
                completeness = non_null_count / len(df) if len(df) > 0 else 0
                stats['completeness'][field_type] = {
                    'percentage': completeness,
                    'missing_count': len(df) - non_null_count
                }
        
        # Análise de qualidade específica
        if 'matricula' in detected_fields:
            col = detected_fields['matricula']
            if col in df.columns:
                unique_count = df[col].nunique()
                duplicate_count = len(df) - unique_count
                stats['data_quality']['matricula_duplicates'] = duplicate_count
        
        return stats

    def generate_recommendations(self, detected_fields: Dict, sheet_type: str) -> List[str]:
        """Gerar recomendações para melhorar a qualidade dos dados"""
        recommendations = []
        
        # Recomendações por tipo de planilha
        if sheet_type == 'UNKNOWN':
            recommendations.append("⚠️  Não foi possível identificar o tipo de planilha automaticamente")
            recommendations.append("💡 Verifique se as colunas têm nomes claros (ex: 'Matrícula', 'Nome')")
        
        if 'matricula' not in detected_fields:
            recommendations.append("🔍 Campo 'Matrícula' não encontrado - essencial para identificar funcionários")
        
        if 'nome' not in detected_fields:
            recommendations.append("👤 Campo 'Nome' não encontrado - necessário para identificação")
        
        if sheet_type == 'ATIVOS' and 'data_admissao' not in detected_fields:
            recommendations.append("📅 Campo 'Data de Admissão' recomendado para funcionários ativos")
        
        if sheet_type == 'DESLIGADOS' and 'data_demissao' not in detected_fields:
            recommendations.append("📅 Campo 'Data de Demissão' obrigatório para funcionários desligados")
        
        if len(detected_fields) < 3:
            recommendations.append("📊 Planilha com poucos campos identificados - adicione mais informações")
        
        return recommendations

    def analyze_multiple_files(self, file_paths: List[str]) -> Dict:
        """Analisar múltiplos arquivos e gerar relatório consolidado"""
        results = {}
        summary = {
            'total_files': len(file_paths),
            'employee_lists': 0,
            'by_type': {},
            'recommendations': []
        }
        
        logger.info(f"📊 Iniciando análise de {len(file_paths)} arquivo(s)...")
        
        for file_path in file_paths:
            result = self.analyze_spreadsheet(file_path)
            results[file_path] = result
            
            if result['is_employee_list']:
                summary['employee_lists'] += 1
                sheet_type = result['sheet_type']
                if sheet_type not in summary['by_type']:
                    summary['by_type'][sheet_type] = 0
                summary['by_type'][sheet_type] += 1
        
        # Gerar recomendações gerais
        if summary['employee_lists'] < len(file_paths):
            summary['recommendations'].append(
                f"⚠️  {len(file_paths) - summary['employee_lists']} arquivo(s) não foram identificados como listas de funcionários"
            )
        
        # Verificar se temos os tipos essenciais
        essential_types = ['ATIVOS', 'FERIAS', 'DESLIGADOS', 'ADMISSAO', 'SINDICATO']
        missing_types = [t for t in essential_types if t not in summary['by_type']]
        
        if missing_types:
            summary['recommendations'].append(
                f"📋 Tipos de planilha não encontrados: {', '.join(missing_types)}"
            )
        
        summary['results'] = results
        
        logger.info(f"✅ Análise concluída: {summary['employee_lists']}/{len(file_paths)} listas de funcionários identificadas")
        
        return summary


def analyze_spreadsheet_tool(file_path: str) -> Dict:
    """Tool function para análise de planilha individual"""
    analyzer = SpreadsheetAnalyzer()
    return analyzer.analyze_spreadsheet(file_path)


def analyze_multiple_spreadsheets_tool(file_paths: List[str]) -> Dict:
    """Tool function para análise de múltiplas planilhas"""
    analyzer = SpreadsheetAnalyzer()
    return analyzer.analyze_multiple_files(file_paths)


if __name__ == "__main__":
    # Exemplo de uso
    analyzer = SpreadsheetAnalyzer()
    
    # Verificar se há arquivos no diretório raw_data
    raw_data_dir = Path("../raw_data")
    if not raw_data_dir.exists():
        # Tentar no diretório atual
        raw_data_dir = Path("raw_data")
    if raw_data_dir.exists():
        excel_files = list(raw_data_dir.glob("*.xlsx")) + list(raw_data_dir.glob("*.xls"))
        
        if excel_files:
            print("🔍 Analisando arquivos encontrados...")
            result = analyzer.analyze_multiple_files([str(f) for f in excel_files])
            
            print("\n" + "="*60)
            print("📊 RELATÓRIO DE ANÁLISE DE PLANILHAS")
            print("="*60)
            
            print(f"\n📁 Total de arquivos: {result['total_files']}")
            print(f"👥 Listas de funcionários: {result['employee_lists']}")
            
            print(f"\n📋 Tipos identificados:")
            for sheet_type, count in result['by_type'].items():
                print(f"   • {sheet_type}: {count} arquivo(s)")
            
            if result['recommendations']:
                print(f"\n💡 Recomendações:")
                for rec in result['recommendations']:
                    print(f"   {rec}")
            
            print(f"\n🔍 Detalhes por arquivo:")
            for file_path, analysis in result['results'].items():
                file_name = Path(file_path).name
                confidence = analysis.get('confidence', 0)
                sheet_type = analysis.get('sheet_type', 'UNKNOWN')
                
                status = "✅" if analysis['is_employee_list'] else "❌"
                print(f"   {status} {file_name}")
                print(f"      Tipo: {sheet_type} (confiança: {confidence:.1%})")
                
                if 'detected_fields' in analysis:
                    fields = ", ".join(analysis['detected_fields'].keys())
                    print(f"      Campos: {fields}")
        else:
            print("❌ Nenhum arquivo Excel encontrado em raw_data/")
    else:
        print("❌ Diretório raw_data/ não encontrado")