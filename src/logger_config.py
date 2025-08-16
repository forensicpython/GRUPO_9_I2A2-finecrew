import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

class ModelThoughtsLogger:
    """Logger especializado para capturar pensamentos do modelo"""
    
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = Path(log_dir) if log_dir else Path(os.path.dirname(__file__)).parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logger específico para pensamentos
        self.thoughts_logger = self._setup_thoughts_logger()
        
        # Configurar logger geral
        self.general_logger = self._setup_general_logger()
    
    def _setup_thoughts_logger(self) -> logging.Logger:
        """Configura logger específico para pensamentos do modelo"""
        logger = logging.getLogger("model_thoughts")
        logger.setLevel(logging.INFO)
        
        # Limpar handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Handler para arquivo de pensamentos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        thoughts_file = self.log_dir / f"model_thoughts_{timestamp}.log"
        
        file_handler = logging.FileHandler(thoughts_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formato específico para pensamentos
        formatter = logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.propagate = False
        
        return logger
    
    def _setup_general_logger(self) -> logging.Logger:
        """Configura logger geral para o sistema"""
        logger = logging.getLogger("finacrew_system")
        logger.setLevel(logging.INFO)
        
        # Limpar handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Handler para arquivo geral
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        general_file = self.log_dir / f"finacrew_log_{timestamp}.log"
        
        file_handler = logging.FileHandler(general_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato para logs gerais
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False
        
        return logger
    
    def log_thought(self, agent_name: str, thought: str):
        """Registra um pensamento do modelo"""
        clean_thought = self._clean_thought(thought)
        if clean_thought:
            self.thoughts_logger.info(f"[{agent_name}] {clean_thought}")
    
    def log_action(self, agent_name: str, action: str, details: str = ""):
        """Registra uma ação do agente"""
        message = f"[{agent_name}] AÇÃO: {action}"
        if details:
            message += f" | {details}"
        self.thoughts_logger.info(message)
    
    def log_observation(self, agent_name: str, observation: str):
        """Registra uma observação do agente"""
        clean_obs = self._clean_thought(observation)
        if clean_obs:
            self.thoughts_logger.info(f"[{agent_name}] OBSERVAÇÃO: {clean_obs}")
    
    def log_system(self, message: str, level: str = "info"):
        """Registra mensagem do sistema"""
        if level.lower() == "error":
            self.general_logger.error(message)
        elif level.lower() == "warning":
            self.general_logger.warning(message)
        else:
            self.general_logger.info(message)
    
    def _clean_thought(self, text: str) -> str:
        """Limpa e formata texto do pensamento"""
        if not text:
            return ""
        
        # Remover prefixos comuns
        text = re.sub(r'^(Thought:|Pensamento:|I need to|Preciso)', '', text, flags=re.IGNORECASE)
        
        # Limpar espaços extras
        text = text.strip()
        
        # Limitar tamanho se muito longo
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text
    
    def get_log_files(self):
        """Retorna lista de arquivos de log criados"""
        return {
            "thoughts": list(self.log_dir.glob("model_thoughts_*.log")),
            "general": list(self.log_dir.glob("finacrew_log_*.log"))
        }

# Instância global do logger
model_logger = ModelThoughtsLogger()