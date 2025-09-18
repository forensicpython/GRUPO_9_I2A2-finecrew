#!/usr/bin/env python3
"""
Agente Analisador de Resultados VR/VA - Alternativa ao Regex
Extrai informações estruturadas do processamento conforme requisitos do PDF
"""

import os
import json
from crewai import Agent, Task, Crew
from crewai.llm import LLM
from crewai_tools import tool
from dotenv import load_dotenv

# Carregar variáveis de ambiente com caminho absoluto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

# Configurar LLM usando a mesma estrutura do projeto
def get_llm():
    # Recarregar variáveis de ambiente para pegar atualizações do header
    load_dotenv(dotenv_path, override=True)

    groq_api_key = os.getenv("GROQ_API_KEY")
    modelo_llm = os.getenv("MODEL", "llama-3.3-70b-versatile")

    print(f"🔑 Chave API carregada: {groq_api_key[:20] if groq_api_key else 'NONE'}...")
    print(f"🤖 Modelo LLM: {modelo_llm}")

    if not groq_api_key:
        raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente")

    if not modelo_llm.startswith('groq/'):
        modelo_llm = f"groq/{modelo_llm}"
    return LLM(model=modelo_llm, api_key=groq_api_key)

@tool
def results_analyzer_agent_tool(raw_processing_result: str) -> str:
    """
    Ferramenta que usa agente para analisar resultados do processamento VR/VA
    em vez de regex, conforme especificações do PDF empresarial.

    Args:
        raw_processing_result: Resultado bruto do processamento VR/VA

    Returns:
        JSON estruturado com dados extraídos pelo agente
    """

    # Configurar agente especializado
    analyzer_agent = Agent(
        role="Analisador de Resultados VR/VA",
        goal="Extrair informações estruturadas do processamento VR/VA conforme requisitos empresariais",
        backstory="""
        Você é um especialista em análise de resultados de processamento de Vale Refeição (VR/VA).
        Seu trabalho é extrair dados precisos conforme as especificações do documento PDF empresarial.

        CONTEXTO EMPRESARIAL:
        - Sistema processa 5 bases: Ativos, Férias, Desligados, Admitidos, Base sindicato x valor
        - Exclui: diretores, estagiários, aprendizes, afastados, funcionários no exterior
        - Regra desligamento: até dia 15 não paga, depois do dia 15 proporcional
        - Cálculo baseado em dias úteis por sindicato
        - Empresa paga 80%, funcionário 20%
        """,
        tools=[],
        llm=get_llm(),
        verbose=True
    )

    # Task de análise estruturada
    analysis_task = Task(
        description=f"""
        Analisar o seguinte resultado de processamento VR/VA e extrair dados estruturados:

        RESULTADO A ANALISAR:
        {raw_processing_result}

        DADOS OBRIGATÓRIOS A EXTRAIR:
        1. funcionarios_elegiveis: número total de funcionários elegíveis ao benefício
        2. valor_total_vr: valor total do Vale Refeição calculado
        3. valor_empresa: valor que a empresa paga (80% do total)
        4. valor_funcionario: valor descontado do funcionário (20% do total)
        5. arquivos_gerados: lista de arquivos Excel criados
        6. tempo_processamento: duração informada do processo

        VALIDAÇÕES CONFORME PDF:
        - Verificar se foram aplicadas regras de sindicato
        - Confirmar exclusões (diretores, estagiários, afastados)
        - Validar regra de desligamento (até dia 15)
        - Verificar cálculo de dias úteis por colaborador
        - Confirmar divisão 80% empresa / 20% funcionário

        IMPORTANTE: Extrair valores numéricos exatos, sem aproximações.
        Se algum valor não for encontrado, retornar 0 para números ou lista vazia para arrays.
        """,
        expected_output="""
        JSON válido com a seguinte estrutura exata:
        {
            "funcionarios_elegiveis": <número_inteiro>,
            "valor_total_vr": <número_decimal>,
            "valor_empresa": <número_decimal>,
            "valor_funcionario": <número_decimal>,
            "arquivos_gerados": [<lista_de_strings>],
            "tempo_processamento": "<string>",
            "validacoes": {
                "regras_sindicato_aplicadas": <true/false>,
                "exclusoes_aplicadas": <true/false>,
                "regra_desligamento_aplicada": <true/false>,
                "divisao_custo_correta": <true/false>
            },
            "metodo_extracao": "agente_analisador"
        }
        """,
        agent=analyzer_agent
    )

    # Executar análise com Crew
    crew = Crew(
        agents=[analyzer_agent],
        tasks=[analysis_task],
        verbose=False
    )

    try:
        result = crew.kickoff()

        # Tentar parsear como JSON
        try:
            parsed_result = json.loads(str(result))
            return json.dumps(parsed_result, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            # Se não for JSON válido, criar estrutura padrão
            return json.dumps({
                "funcionarios_elegiveis": 0,
                "valor_total_vr": 0.0,
                "valor_empresa": 0.0,
                "valor_funcionario": 0.0,
                "arquivos_gerados": [],
                "tempo_processamento": "erro_na_analise",
                "validacoes": {
                    "regras_sindicato_aplicadas": False,
                    "exclusoes_aplicadas": False,
                    "regra_desligamento_aplicada": False,
                    "divisao_custo_correta": False
                },
                "metodo_extracao": "agente_analisador",
                "erro": "Falha no parsing do resultado do agente",
                "resultado_bruto": str(result)
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        # Em caso de erro, retornar estrutura de erro
        return json.dumps({
            "funcionarios_elegiveis": 0,
            "valor_total_vr": 0.0,
            "valor_empresa": 0.0,
            "valor_funcionario": 0.0,
            "arquivos_gerados": [],
            "tempo_processamento": "erro_execucao",
            "validacoes": {
                "regras_sindicato_aplicadas": False,
                "exclusoes_aplicadas": False,
                "regra_desligamento_aplicada": False,
                "divisao_custo_correta": False
            },
            "metodo_extracao": "agente_analisador",
            "erro": f"Erro na execução do agente: {str(e)}"
        }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Teste da ferramenta
    test_result = """
    ✅ Funcionários elegíveis: 1719
    💵 Valor total VR: R$ 1.385.943,75
    🏢 Valor empresa (80%): R$ 1.108.755,00
    👤 Valor funcionário (20%): R$ 277.188,75
    📁 Arquivos gerados: ['VR MENSAL 05.2025.xlsx', 'FUNCIONARIOS_EXCLUIDOS_AUDITORIA.xlsx']
    ⏱️ Tempo de processamento: Real-time
    """

    result = results_analyzer_agent_tool.func(test_result)
    print("🧪 Teste do Agente Analisador:")
    print(result)