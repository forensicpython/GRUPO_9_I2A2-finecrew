#!/usr/bin/env python3
"""
Ferramenta para capturar e salvar logs das conversas dos agentes
Cria um arquivo de log detalhado com todas as interações dos agentes
"""

import os
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from crewai_tools import tool
from io import StringIO


class AgentLogCapture:
    """Captura logs dos agentes CrewAI"""

    def __init__(self):
        self.logs = []
        self.start_time = datetime.now()
        self.log_file = None

    def start_capture(self, session_id=None):
        """Inicia a captura de logs"""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Criar diretório de logs se não existir
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        self.log_file = logs_dir / f"agentes_log_{session_id}.txt"

        # Configurar logging para capturar saídas dos agentes
        self.setup_logging()

        # Log inicial
        self.add_log("SISTEMA", "Iniciando captura de logs dos agentes", "INFO")

    def setup_logging(self):
        """Configura logging para capturar outputs dos agentes"""
        # Capturar prints e logs do sistema
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()

    def add_log(self, agent_role, message, level="INFO"):
        """Adiciona uma entrada no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "agent": agent_role,
            "level": level,
            "message": message
        }
        self.logs.append(log_entry)

        # Escrever no arquivo se disponível
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {level} - {agent_role}: {message}\n")

    def capture_crew_execution(self, crew_result, crew_info="FinaCrew"):
        """Captura resultado da execução do crew"""
        self.add_log("CREW_RESULT", f"Resultado do {crew_info}: {str(crew_result)}", "RESULT")

        # Tentar extrair informações detalhadas se disponível
        if hasattr(crew_result, 'tasks_output'):
            for i, task_output in enumerate(crew_result.tasks_output):
                self.add_log(f"TASK_{i+1}", f"Output: {task_output.description}", "TASK")
                if hasattr(task_output, 'agent'):
                    self.add_log(f"AGENT_{task_output.agent.role}", f"Executou: {task_output.description}", "EXECUTION")

    def save_final_log(self):
        """Salva o log final em formato estruturado"""
        if not self.log_file:
            return None

        # Criar arquivo JSON com estrutura completa
        json_file = self.log_file.with_suffix('.json')

        log_summary = {
            "session_info": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "total_logs": len(self.logs)
            },
            "logs": self.logs,
            "summary": {
                "agents_involved": list(set([log["agent"] for log in self.logs])),
                "log_levels": list(set([log["level"] for log in self.logs]))
            }
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(log_summary, f, ensure_ascii=False, indent=2)

        self.add_log("SISTEMA", f"Log salvo em: {self.log_file} e {json_file}", "INFO")

        return str(self.log_file)


# Instância global para captura
agent_logger = AgentLogCapture()


@tool
def agent_logger_tool(action: str, data: str = "", agent_role: str = "UNKNOWN") -> str:
    """
    Ferramenta para capturar logs das conversas dos agentes.

    Args:
        action: Ação a executar (start, log, save)
        data: Dados ou mensagem para logar
        agent_role: Role do agente que está logando

    Returns:
        Status da operação ou caminho do arquivo salvo
    """

    try:
        if action == "start":
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_logger.start_capture(session_id)
            return f"Captura iniciada - Sessão: {session_id}"

        elif action == "log":
            agent_logger.add_log(agent_role, data, "LOG")
            return "Log adicionado com sucesso"

        elif action == "crew_result":
            agent_logger.capture_crew_execution(data, agent_role)
            return "Resultado do crew capturado"

        elif action == "save":
            log_file = agent_logger.save_final_log()
            if log_file:
                return log_file
            else:
                return "Nenhum log para salvar"

        else:
            return f"Ação não reconhecida: {action}"

    except Exception as e:
        return f"Erro na ferramenta de log: {str(e)}"


def capture_agent_conversation(func):
    """Decorator para capturar conversas de agentes"""
    def wrapper(*args, **kwargs):
        # Iniciar captura
        agent_logger_tool.func("start", "", "DECORATOR")

        try:
            # Executar função original
            result = func(*args, **kwargs)

            # Capturar resultado
            agent_logger_tool.func("crew_result", str(result), func.__name__)

            return result
        finally:
            # Salvar logs
            agent_logger_tool.func("save", "", "DECORATOR")

    return wrapper


if __name__ == "__main__":
    # Teste da ferramenta
    print("🧪 Testando Agent Logger Tool...")

    # Iniciar sessão
    result = agent_logger_tool.func("start")
    print(f"Início: {result}")

    # Adicionar alguns logs de teste
    agent_logger_tool.func("log", "Iniciando análise de dados VR/VA", "Analisador VR/VA")
    agent_logger_tool.func("log", "Processando 1719 funcionários", "Processador de Dados")
    agent_logger_tool.func("log", "Cálculo concluído: R$ 1.385.943,75", "Calculadora VR")

    # Salvar
    log_file = agent_logger_tool.func("save")
    print(f"Log salvo em: {log_file}")