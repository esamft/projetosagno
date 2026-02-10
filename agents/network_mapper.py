"""
Agente Mapeador de Rede

Especializado em analisar a estrutura da rede de contatos,
identificar clusters, gaps e oportunidades de networking.
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from loguru import logger

from config.settings import DEFAULT_MODEL
from config.crm_profiles import get_agent_instructions
from storage.crm_store import load_profile

from tools.contact_manager import (
    crm_list_all_contacts,
    crm_search_contacts,
    crm_get_contact_details,
    crm_get_stats,
)
from tools.network_analyzer import (
    crm_analyze_network,
    crm_get_relationship_report,
)
from tools.relationship_scorer import (
    crm_score_all_relationships,
)


def create_network_mapper() -> Agent:
    """
    Cria o agente Mapeador de Rede.

    Este agente e responsavel por:
    - Mapear a estrutura da rede de contatos
    - Identificar clusters por empresa, cidade, categoria
    - Detectar gaps na rede (categorias sem representantes)
    - Sugerir expansoes estrategicas da rede
    - Analisar diversidade e resiliencia da rede

    Returns:
        Agent configurado como Mapeador de Rede
    """
    profile = load_profile()
    tipo = profile.get("tipo", "custom") if profile else "custom"
    instrucoes_perfil = get_agent_instructions(tipo)

    agent = Agent(
        name="Mapeador de Rede",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Especialista em mapear e analisar a estrutura da rede de "
            "relacionamentos, identificando gaps e oportunidades"
        ),
        instructions=[
            "# Role",
            "Voce e um Mapeador de Rede especializado em analisar a estrutura "
            "e qualidade da rede de relacionamentos do usuario.",
            "",
            "# Contexto do Perfil",
            instrucoes_perfil,
            "",
            "# Suas Responsabilidades",
            "1. Mapear a estrutura completa da rede de contatos",
            "2. Identificar clusters (grupos naturais por empresa, cidade, etc)",
            "3. Detectar gaps criticos na rede para o perfil do usuario",
            "4. Avaliar diversidade e resiliencia da rede",
            "5. Sugerir expansoes estrategicas alinhadas aos objetivos",
            "",
            "# Como Trabalhar",
            "1. Use crm_analyze_network() para a analise completa da rede",
            "2. Use crm_list_all_contacts() para ver todos os contatos",
            "3. Use crm_search_contacts() para explorar segmentos especificos",
            "4. Use crm_score_all_relationships() para cruzar com saude",
            "5. Use crm_get_stats() para metricas gerais",
            "",
            "# Formato de Resposta",
            "- Apresente um mapa visual da rede usando texto/markdown",
            "- Use tabelas para mostrar distribuicoes",
            "- Destaque gaps criticos com acoes sugeridas",
            "- Mostre clusters e conexoes entre grupos",
            "- Sugira 3-5 acoes estrategicas para fortalecer a rede",
            "",
            "# Conceitos de Analise de Rede",
            "- Diversidade: quantas categorias diferentes estao representadas",
            "- Concentracao: se a rede depende de poucos contatos-chave",
            "- Gaps: categorias prioritarias sem representantes",
            "- Clusters: grupos de contatos conectados (mesma empresa, cidade, etc)",
            "- Resiliencia: capacidade da rede de se manter se perder contatos-chave",
            "",
            "# Regras",
            "- SEMPRE use crm_analyze_network() como primeira ferramenta",
            "- Base suas analises em dados reais, nao suposicoes",
            "- Considere o perfil do usuario ao identificar gaps",
            "- Seja estrategico nas sugestoes de expansao",
        ],
        tools=[
            crm_analyze_network,
            crm_get_relationship_report,
            crm_score_all_relationships,
            crm_list_all_contacts,
            crm_search_contacts,
            crm_get_contact_details,
            crm_get_stats,
        ],
        markdown=True,
        show_tool_calls=True,
    )

    logger.info(f"Agente '{agent.name}' criado")
    return agent
