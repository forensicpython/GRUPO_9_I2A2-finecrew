from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
#from crewai.tools import tool
from dotenv import load_dotenv
from crewai.llm import LLM
from tools.math_tool import multiplication_tool
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Carrega variáveis de ambiente
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
modelo_llm = os.getenv("MODEL")
llm = LLM(model=modelo_llm)

# Sua ferramenta personalizada

@CrewBase
class Professor:
    """Crew de professores para ensinar multiplicação"""
    
    agents_config = 'config/agents.yaml'
    tasks_config  = 'config/tasks.yaml'

    @agent
    def generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['generator_agent'],
            llm=llm,
            verbose=True
        )

    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['writer_agent'],
            llm=llm,
            tools=[multiplication_tool],
            verbose=True
        )

    @task
    def generate_numbers_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_numbers_task'],
            agent=self.generator_agent()  # ✅ Agora está instanciando
    )
       

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            agent=self.writer_agent(),
            tools=[multiplication_tool],
            output_file="report.html",
            context=[self.generate_numbers_task()]  # também precisa ser chamado
    )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

