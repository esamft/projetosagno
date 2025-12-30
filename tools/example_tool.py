"""
Exemplo de tool simples
"""
from typing import Optional


def example_tool(query: str, option: Optional[str] = None) -> str:
    """
    Ferramenta de exemplo que processa uma consulta

    Esta é uma tool de exemplo que demonstra como criar
    ferramentas para os agentes Agno.

    Args:
        query: Consulta a ser processada
        option: Opção adicional (opcional)

    Returns:
        Resultado do processamento em formato string
    """
    result = f"Processando query: {query}"

    if option:
        result += f"\nOpção aplicada: {option}"

    return result
