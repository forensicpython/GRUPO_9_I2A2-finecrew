#!/usr/bin/env python3
"""
AGENTE FILE MANAGER - FinaCrew Sistema Multi-Agente
Responsável por normalizar nomes de arquivos e gerenciar acessos seguros
"""

import os
import shutil
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import logging

class FileManagerAgent:
    """Agente responsável por gerenciar e normalizar arquivos"""

    def __init__(self, raw_data_dir: str):
        self.raw_data_dir = Path(raw_data_dir)
        self.file_mapping = {}
        self.logger = logging.getLogger(__name__)

    def normalize_filenames(self) -> Dict[str, str]:
        """
        Normaliza nomes de arquivos removendo espaços e acentos
        Retorna mapeamento: nome_original -> nome_normalizado
        """
        mappings = {
            # Mapeamento de nomes com espaços/acentos para nomes normalizados
            "ADMISSÃO ABRIL.xlsx": "ADMISSAO_ABRIL.xlsx",
            "FÉRIAS.xlsx": "FERIAS.xlsx",
            "ESTÁGIO.xlsx": "ESTAGIO.xlsx",
            "Base dias uteis.xlsx": "Base_dias_uteis.xlsx",
            "Base sindicato x valor.xlsx": "Base_sindicato_x_valor.xlsx",
            "VR MENSAL 05.2025.xlsx": "VR_MENSAL_05_2025.xlsx"
        }

        print("🗂️ Agente File Manager: Normalizando nomes de arquivos...")

        for original_name, normalized_name in mappings.items():
            original_path = self.raw_data_dir / original_name
            normalized_path = self.raw_data_dir / normalized_name

            if original_path.exists() and not normalized_path.exists():
                try:
                    shutil.copy2(original_path, normalized_path)
                    self.file_mapping[normalized_name] = str(normalized_path)
                    print(f"✅ Normalizado: {original_name} -> {normalized_name}")
                except Exception as e:
                    print(f"❌ Erro ao normalizar {original_name}: {e}")
            elif normalized_path.exists():
                self.file_mapping[normalized_name] = str(normalized_path)
                print(f"✅ Já existe: {normalized_name}")

        # Mapear arquivos que já estão com nomes corretos
        correct_files = [
            "ATIVOS.xlsx", "DESLIGADOS.xlsx", "AFASTAMENTOS.xlsx",
            "APRENDIZ.xlsx", "EXTERIOR.xlsx"
        ]

        for filename in correct_files:
            file_path = self.raw_data_dir / filename
            if file_path.exists():
                self.file_mapping[filename] = str(file_path)
                print(f"✅ Arquivo correto: {filename}")

        print(f"📋 File Manager: {len(self.file_mapping)} arquivos mapeados")
        return self.file_mapping

    def get_file_path(self, filename: str) -> str:
        """
        Retorna caminho completo para arquivo, tratando variações de nome
        """
        # Tentar nome exato primeiro
        if filename in self.file_mapping:
            return self.file_mapping[filename]

        # Tentar variações comuns
        variations = {
            "FÉRIAS.xlsx": ["FERIAS.xlsx"],
            "ADMISSÃO ABRIL.xlsx": ["ADMISSAO_ABRIL.xlsx"],
            "ESTÁGIO.xlsx": ["ESTAGIO.xlsx"],
            "Base sindicato x valor.xlsx": ["Base_sindicato_x_valor.xlsx"],
            "Base dias uteis.xlsx": ["Base_dias_uteis.xlsx"]
        }

        for original, alts in variations.items():
            if filename == original:
                for alt in alts:
                    if alt in self.file_mapping:
                        return self.file_mapping[alt]

        # Se não encontrou, retornar caminho direto
        direct_path = self.raw_data_dir / filename
        if direct_path.exists():
            return str(direct_path)

        raise FileNotFoundError(f"Arquivo não encontrado: {filename}")

    def load_excel_safe(self, filename: str, sheet_name: str = None) -> pd.DataFrame:
        """
        Carrega Excel de forma segura, tratando encoding e formatos
        """
        try:
            file_path = self.get_file_path(filename)

            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)

            print(f"📊 Carregado {filename}: {len(df)} registros")
            return df

        except Exception as e:
            print(f"❌ Erro ao carregar {filename}: {e}")
            raise

    def get_available_files(self) -> List[str]:
        """Retorna lista de arquivos disponíveis"""
        return list(self.file_mapping.keys())

    def validate_required_files(self) -> Tuple[bool, List[str]]:
        """
        Valida se todos os arquivos obrigatórios estão disponíveis
        """
        required_files = [
            "ATIVOS.xlsx",
            "FERIAS.xlsx",
            "DESLIGADOS.xlsx",
            "ADMISSAO_ABRIL.xlsx",
            "Base_sindicato_x_valor.xlsx",
            "Base_dias_uteis.xlsx"
        ]

        missing_files = []
        for required_file in required_files:
            try:
                self.get_file_path(required_file)
            except FileNotFoundError:
                missing_files.append(required_file)

        all_present = len(missing_files) == 0

        if all_present:
            print("✅ File Manager: Todos os arquivos obrigatórios encontrados")
        else:
            print(f"❌ File Manager: Arquivos faltantes: {missing_files}")

        return all_present, missing_files

# Função utilitária para uso em outros agentes
def get_file_manager(raw_data_dir: str = None) -> FileManagerAgent:
    """Retorna instância configurada do File Manager Agent"""
    if raw_data_dir is None:
        raw_data_dir = "/mnt/b3f9265b-b14c-43a0-adbb-51ada5f71808/Curso I2A2/FinaCrew/raw_data"

    manager = FileManagerAgent(raw_data_dir)
    manager.normalize_filenames()
    return manager