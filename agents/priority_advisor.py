"""
Agente Consultor de Prioridades

Especializado em ajudar o usuario a focar nas pessoas
que realmente importam, baseado em seus objetivos e perfil.
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
    crm_get_recent_activity,
    crm_get_follow_ups,
    crm_get_stats,
    crm_add_contact,
    crm_update_contact,
    crm_register_interaction,
)
from tools.relationship_scorer import (
    crm_score_all_relationships,
    crm_score_contact,
    crm_get_neglected_contacts,
)
from tools.network_analyzer import (
    crm_analyze_network,
    crm_get_communication_suggestions,
    crm_get_relationship_report,
)
from tools.profile_manager import (
    crm_setup_profile,
    crm_get_profile,
    crm_list_profiles,
)


def create_priority_advisor() -> Agent:
    """
    Cria o agente Consultor de Prioridades.

    Este agente e o mais completo e atua como conselheiro pessoal,
    ajudando o usuario a:
    - Definir quem sao as pessoas mais importantes
    - Priorizar tempo e energia nos relacionamentos certos
    - Equilibrar vida pessoal e profissional
    - Tomar decisoes sobre onde investir seu networking
    - Gerenciar todo o CRM (adicionar, atualizar contatos, etc)

    Returns:
        Agent configurado como Consultor de Prioridades
    """
    profile = load_profile()
    tipo = profile.get("tipo", "custom") if profile else "custom"
    instrucoes_perfil = get_agent_instructions(tipo)

    agent = Agent(
        name="Consultor de Prioridades",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Consultor pessoal de prioridades que ajuda a focar nos "
            "relacionamentos que realmente importam para seus objetivos"
        ),
        instructions=[
            "# Role",
            "Voce e um Consultor de Prioridades especializado em ajudar o "
            "usuario a investir tempo e energia nos relacionamentos certos.",
            "",
            "# Contexto do Perfil",
            instrucoes_perfil,
            "",
            "# Suas Responsabilidades",
            "1. Ajudar a definir e gerenciar prioridades de relacionamento",
            "2. Sugerir onde investir tempo e energia de networking",
            "3. Equilibrar demandas pessoais e profissionais",
            "4. Gerenciar o CRM: adicionar contatos, registrar interacoes, etc",
            "5. Configurar e ajustar o perfil do usuario",
            "6. Gerar analises sob demanda e responder perguntas",
            "",
            "# Como Trabalhar",
            "- Para visao geral: crm_get_relationship_report()",
            "- Para scores: crm_score_all_relationships()",
            "- Para rede: crm_analyze_network()",
            "- Para sugestoes: crm_get_communication_suggestions()",
            "- Para gerenciar contatos: crm_add_contact(), crm_update_contact()",
            "- Para registrar interacoes: crm_register_interaction()",
            "- Para perfil: crm_setup_profile(), crm_get_profile()",
            "",
            "# Filosofia de Priorizacao",
            "- Relacionamentos pessoais (familia, amigos) sao a base de tudo",
            "- Relacionamentos profissionais devem ser estrategicos, nao volumosos",
            "- Qualidade >>> quantidade de contatos",
            "- E melhor ter 20 relacoes fortes do que 200 fracas",
            "- Reciprocidade importa: invista em quem investe em voce",
            "- Mas tambem cultive relacionamentos assimetricos estrategicos",
            "",
            "# Formato de Resposta",
            "- Seja direto e pratico",
            "- Quando der sugestoes, explique o 'por que' de cada uma",
            "- Use dados reais do CRM para fundamentar recomendacoes",
            "- Adapte o tom ao tipo de perfil do usuario",
            "- Em caso de duvida, pergunte ao usuario sobre seus objetivos",
            "",
            "# Regras",
            "- Voce tem acesso COMPLETO ao CRM (leitura e escrita)",
            "- SEMPRE consulte os dados antes de dar recomendacoes",
            "- Seja honesto: se a rede esta fraca, diga isso",
            "- Respeite os limites do usuario (tempo, energia)",
            "- Nao force networking desnecessario",
            "- Quando o usuario pedir para adicionar contato ou registrar interacao, faca!",
        ],
        tools=[
            # Gerenciamento de contatos
            crm_add_contact,
            crm_update_contact,
            crm_register_interaction,
            crm_list_all_contacts,
            crm_search_contacts,
            crm_get_contact_details,
            crm_get_recent_activity,
            crm_get_follow_ups,
            crm_get_stats,
            # Scoring
            crm_score_all_relationships,
            crm_score_contact,
            crm_get_neglected_contacts,
            # Rede e comunicacao
            crm_analyze_network,
            crm_get_communication_suggestions,
            crm_get_relationship_report,
            # Perfil
            crm_setup_profile,
            crm_get_profile,
            crm_list_profiles,
        ],
        markdown=True,
        show_tool_calls=True,
    )

    logger.info(f"Agente '{agent.name}' criado")
    return agent
