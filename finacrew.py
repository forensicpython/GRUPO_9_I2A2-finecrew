#!/usr/bin/env python3
"""
FinaCrew - Sistema Multi-Agente para Cálculo de VR
Migração para filosofia CrewAI com decoradores e YAMLs
"""

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from crewai.llm import LLM
from dotenv import load_dotenv
import sys
import os
from pathlib import Path

# Adicionar tools ao path
current_dir = Path(__file__).parent
tools_dir = current_dir / "tools"
sys.path.insert(0, str(tools_dir))

# Importar tools convertidas
from tools.spreadsheet_analyzer_tool import spreadsheet_analyzer_tool
from tools.model_excel_generator_tool import model_excel_generator_tool
from tools.working_days_calculator_tool import working_days_calculator_tool
from tools.file_discovery_tool import file_discovery_tool
from tools.real_data_processor_tool import real_data_processor_tool

# Carrega variáveis de ambiente
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
modelo_llm = os.getenv("MODEL", "llama-3.3-70b-versatile")
# Adicionar provider para CrewAI
if not modelo_llm.startswith('groq/'):
    modelo_llm = f"groq/{modelo_llm}"
llm = LLM(model=modelo_llm, api_key=groq_api_key)

@CrewBase
class FinaCrew:
    """
    Crew FinaCrew para cálculo automatizado de VR/VA

    Sistema multi-agente que processa planilhas de funcionários
    e gera cálculos de Vale Refeição conforme especificações do projeto.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def file_manager_agent(self) -> Agent:
        """Agente especialista em normalização e carregamento de dados"""
        return Agent(
            config=self.agents_config['file_manager_agent'],
            llm=llm,
            tools=[file_discovery_tool, spreadsheet_analyzer_tool],
            verbose=True
        )

    @agent
    def exclusions_agent(self) -> Agent:
        """Agente especialista em regras de negócio e exclusões"""
        return Agent(
            config=self.agents_config['exclusions_agent'],
            llm=llm,
            tools=[working_days_calculator_tool],
            verbose=True
        )

    @agent
    def coordinator_agent(self) -> Agent:
        """Agente coordenador principal do processo"""
        return Agent(
            config=self.agents_config['coordinator_agent'],
            llm=llm,
            tools=[
                real_data_processor_tool,
                spreadsheet_analyzer_tool,
                model_excel_generator_tool,
                working_days_calculator_tool
            ],
            verbose=True
        )

    @task
    def consolidate_base_task(self) -> Task:
        """Task para consolidação da base de dados"""
        return Task(
            config=self.tasks_config['consolidate_base_task'],
            agent=self.file_manager_agent()
        )

    @task
    def apply_exclusions_task(self) -> Task:
        """Task para aplicação de filtros de exclusão"""
        return Task(
            config=self.tasks_config['apply_exclusions_task'],
            agent=self.exclusions_agent(),
            context=[self.consolidate_base_task()]
        )

    @task
    def calculate_working_days_task(self) -> Task:
        """Task para cálculo de dias úteis por região"""
        return Task(
            config=self.tasks_config['calculate_working_days_task'],
            agent=self.exclusions_agent(),
            tools=[working_days_calculator_tool],
            context=[self.apply_exclusions_task()]
        )

    @task
    def calculate_vr_values_task(self) -> Task:
        """Task para cálculo de valores VR"""
        return Task(
            config=self.tasks_config['calculate_vr_values_task'],
            agent=self.coordinator_agent(),
            context=[self.calculate_working_days_task()]
        )

    @task
    def generate_final_reports_task(self) -> Task:
        """Task para geração de relatórios finais"""
        return Task(
            config=self.tasks_config['generate_final_reports_task'],
            agent=self.coordinator_agent(),
            tools=[model_excel_generator_tool],
            output_file="VR MENSAL 05.2025.xlsx",
            context=[self.calculate_vr_values_task()]
        )

    @crew
    def crew(self) -> Crew:
        """Orquestração principal do sistema FinaCrew"""
        import os
        # Definir o LLM para o crew
        os.environ["OPENAI_API_KEY"] = "não-usado"  # CrewAI pede, mas usamos Groq

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            max_execution_time=1800,  # 30 minutos
            manager_llm=llm  # Usar Groq como LLM principal
        )

# Função de conveniência para executar o processo
def process_vr_calculation(month: str = "05", year: str = "2025") -> dict:
    """
    Executa o processo completo de cálculo de VR

    Args:
        month: Mês de referência (padrão: "05")
        year: Ano de referência (padrão: "2025")

    Returns:
        dict: Resultado do processamento
    """
    try:
        print(f"\n🚀 FINACREW CREWAI: Iniciando sistema multi-agente para cálculo VR {month}/{year}")
        print(f"=" * 80)
        print(f"📋 AGENTES CONFIGURADOS:")
        print(f"   🤖 Gerenciador de Arquivos - Normalização e carregamento")
        print(f"   🤖 Filtro de Elegibilidade - Regras de negócio e exclusões")
        print(f"   🤖 Coordenador Principal - Orquestração e cálculos")
        print(f"=" * 80)

        print(f"\n📦 TASKS CONFIGURADAS:")
        print(f"   📋 1. Consolidação da Base de Dados")
        print(f"   📋 2. Aplicação de Filtros de Exclusão")
        print(f"   📋 3. Cálculo de Dias Úteis por Região")
        print(f"   📋 4. Cálculo de Valores VR")
        print(f"   📋 5. Geração de Relatórios Finais")
        print(f"=" * 80)

        # Inicializar FinaCrew
        print(f"\n🔧 Inicializando FinaCrew com decoradores e YAMLs...")
        finacrew = FinaCrew()

        # Verificar agentes criados
        print(f"\n👥 AGENTES INSTANCIADOS:")
        try:
            crew_instance = finacrew.crew()
            if hasattr(crew_instance, 'agents'):
                for i, agent in enumerate(crew_instance.agents, 1):
                    print(f"   {i}. {agent.name} - {agent.role}")
                    print(f"      Goal: {agent.goal[:60]}...")
                    print(f"      Tools: {[tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in agent.tools]}")
            else:
                print(f"   ✅ 3 agentes configurados via decoradores YAML")

            print(f"\n📝 TASKS INSTANCIADAS:")
            if hasattr(crew_instance, 'tasks'):
                for i, task in enumerate(crew_instance.tasks, 1):
                    print(f"   {i}. {task.name}")
                    print(f"      Agent: {task.agent.name}")
                    print(f"      Description: {task.description[:60]}...")
            else:
                print(f"   ✅ 5 tasks configuradas via decoradores YAML")
        except Exception as e:
            print(f"   ⚠️ Erro ao acessar detalhes dos agentes: {e}")
            print(f"   ✅ Agentes e tasks configurados via decoradores YAML")

        print(f"\n🎬 INICIANDO EXECUÇÃO SEQUENCIAL DOS AGENTES...")
        print(f"=" * 80)

        # Executar processo com logs detalhados
        result = finacrew.crew().kickoff()

        print(f"\n" + "=" * 80)
        print(f"✅ FINACREW CREWAI: Processamento concluído com sucesso!")
        print(f"📊 Tipo do resultado: {type(result)}")
        if hasattr(result, 'raw'):
            print(f"📄 Resultado bruto: {str(result.raw)[:200]}...")
        else:
            print(f"📄 Resultado: {str(result)[:200]}...")
        print(f"=" * 80)

        return {
            "success": True,
            "result": result,
            "month": month,
            "year": year
        }

    except Exception as e:
        print(f"\n" + "=" * 80)
        print(f"❌ FINACREW CREWAI: Erro no processamento!")
        print(f"🚨 Erro: {e}")
        print(f"🔍 Tipo do erro: {type(e)}")
        import traceback
        print(f"📋 Stack trace:")
        traceback.print_exc()
        print(f"=" * 80)
        return {
            "success": False,
            "error": str(e),
            "month": month,
            "year": year
        }

if __name__ == "__main__":
    # Execução direta para testes
    result = process_vr_calculation()
    print(f"Resultado final: {result}")