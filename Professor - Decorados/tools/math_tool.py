from crewai.tools import tool

# Definindo a classe MultiplicationTool com decoradores
@tool("multiplication_tool")
def multiplication_tool(primeiro_numero: int, segundo_numero: int) -> str:
    """
    Realiza a multiplicação de dois números inteiros e retorna o resultado de forma descritiva.
    Esta ferramenta é útil para tarefas educacionais ou situações em que se deseja apresentar
    o resultado de uma multiplicação com linguagem explicativa.
    """
    try:
        # Validação explícita
        if not isinstance(primeiro_numero, int) or not isinstance(segundo_numero, int):
            return "Erro: ambos os valores devem ser números inteiros."

        resultado = primeiro_numero * segundo_numero

        return (
            f"Multiplicando {primeiro_numero} por {segundo_numero}, temos:\n"
            f"{primeiro_numero} x {segundo_numero} = {resultado}.\n"
            "A multiplicação está correta e completa. 👍"
        )

    except Exception as e:
        return f"Ocorreu um erro durante a multiplicação: {str(e)}"
