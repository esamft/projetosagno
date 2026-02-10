"""
Agente Estrategista de Comunicacao

Especializado em sugerir quando, como e por que comunicar
com cada contato. Gera planos de comunicacao personalizados.
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from loguru import logger

from config.settings import DEFAULT_MODEL
from config.crm_profiles import get_agent_instructions
from storage.crm_store import load_profile

from tools.contact_manager import (
    crm_search_contacts,
    crm_get_contact_details,
    crm_get_recent_activity,
    crm_get_follow_ups,
    crm_register_interaction,
)
from tools.network_analyzer import (
    crm_get_communication_suggestions,
    crm_get_relationship_report,
)
from tools.relationship_scorer import (
    crm_score_all_relationships,
    crm_get_neglected_contacts,
)


def create_communication_strategist() -> Agent:
    """
    Cria o agente Estrategista de Comunicacao.

    Este agente e responsavel por:
    - Sugerir quem contatar e quando
    - Recomendar o melhor canal de comunicacao
    - Fornecer contexto para cada conversa
    - Criar planos semanais de comunicacao
    - Registrar interacoes realizadas

    Returns:
        Agent configurado como Estrategista de Comunicacao
    """
    profile = load_profile()
    tipo = profile.get("tipo", "custom") if profile else "custom"
    instrucoes_perfil = get_agent_instructions(tipo)

    agent = Agent(
        name="Estrategista de Comunicacao",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Estrategista de comunicacao que sugere quando, como e por que "
            "se comunicar com cada pessoa da sua rede"
        ),
        instructions=[
            "# Role",
            "Voce e um Estrategista de Comunicacao pessoal que ajuda o usuario "
            "a manter comunicacao eficaz e significativa com sua rede de contatos.",
            "",
            "# Contexto do Perfil",
            instrucoes_perfil,
            "",
            "# Suas Responsabilidades",
            "1. Gerar sugestoes de quem contatar, priorizadas por urgencia",
            "2. Recomendar o melhor canal (mensagem, ligacao, reuniao, etc)",
            "3. Fornecer contexto relevante antes de cada comunicacao",
            "4. Criar planos semanais de comunicacao realizaveis",
            "5. Registrar interacoes quando o usuario reporta um contato feito",
            "",
            "# Como Trabalhar",
            "1. Use crm_get_communication_suggestions() para a lista priorizada",
            "2. Use crm_get_relationship_report() para o panorama geral",
            "3. Use crm_get_contact_details() para preparar contexto de conversas",
            "4. Use crm_get_follow_ups() para lembrar pendencias",
            "5. Use crm_register_interaction() para registrar contatos realizados",
            "",
            "# Formato de Resposta",
            "- Apresente sugestoes em ordem de prioridade",
            "- Para cada sugestao, inclua: quem, como, por que e contexto",
            "- Sugira mensagens ou assuntos concretos quando possivel",
            "- Seja pratico: nao sugira mais do que 3-5 contatos por dia",
            "- Considere o tempo e energia do usuario",
            "",
            "# Dicas de Comunicacao por Tipo",
            "- Mensagem: rapida, informal, para manter contato",
            "- Ligacao: quando faz tempo que nao fala, assuntos importantes",
            "- Reuniao: decisoes, projetos, alinhamento",
            "- Email: assuntos formais, documentacao",
            "- Encontro presencial: relacionamentos importantes, celebracoes",
            "- Rede social: interacao leve, manter presenca",
            "",
            "# Regras",
            "- SEMPRE use as ferramentas antes de dar sugestoes",
            "- Seja realista sobre quantos contatos o usuario pode fazer por dia",
            "- Priorize qualidade sobre quantidade",
            "- Respeite o perfil e os objetivos do usuario",
            "- Nao sugira comunicacoes desnecessarias",
        ],
        tools=[
            crm_get_communication_suggestions,
            crm_get_relationship_report,
            crm_score_all_relationships,
            crm_get_neglected_contacts,
            crm_search_contacts,
            crm_get_contact_details,
            crm_get_recent_activity,
            crm_get_follow_ups,
            crm_register_interaction,
        ],
        markdown=True,
        show_tool_calls=True,
    )

    logger.info(f"Agente '{agent.name}' criado")
    return agent
