"""
Agente Analista de Relacionamentos

Especializado em analisar a saude dos relacionamentos,
calcular scores, identificar tendencias e gerar alertas.
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from loguru import logger

from config.settings import DEFAULT_MODEL
from config.crm_profiles import get_agent_instructions
from storage.crm_store import load_profile

from tools.contact_manager import (
    crm_list_all_contacts,
    crm_get_contact_details,
    crm_get_recent_activity,
    crm_get_follow_ups,
    crm_get_stats,
)
from tools.relationship_scorer import (
    crm_score_all_relationships,
    crm_score_contact,
    crm_get_neglected_contacts,
)


def create_relationship_analyst() -> Agent:
    """
    Cria o agente Analista de Relacionamentos.

    Este agente e responsavel por:
    - Avaliar a saude de cada relacionamento (score 0-100)
    - Identificar relacionamentos esfriando ou perdidos
    - Gerar alertas para contatos negligenciados
    - Analisar tendencias (melhorando/piorando)
    - Recomendar acoes para fortalecer vinculos

    Returns:
        Agent configurado como Analista de Relacionamentos
    """
    profile = load_profile()
    tipo = profile.get("tipo", "custom") if profile else "custom"
    instrucoes_perfil = get_agent_instructions(tipo)

    agent = Agent(
        name="Analista de Relacionamentos",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Analista especializado em avaliar a saude dos relacionamentos, "
            "identificar padroes e recomendar acoes para fortalecer vinculos"
        ),
        instructions=[
            "# Role",
            "Voce e um Analista de Relacionamentos especializado em avaliar a saude "
            "e qualidade dos vinculos interpessoais do usuario.",
            "",
            "# Contexto do Perfil",
            instrucoes_perfil,
            "",
            "# Suas Responsabilidades",
            "1. Avaliar o score de saude de cada relacionamento (0-100)",
            "2. Identificar relacionamentos que estao esfriando ou foram perdidos",
            "3. Gerar alertas para contatos negligenciados",
            "4. Analisar tendencias: quais relacoes estao melhorando ou piorando",
            "5. Recomendar acoes concretas para fortalecer vinculos importantes",
            "",
            "# Como Trabalhar",
            "1. Comece usando crm_score_all_relationships() para ter uma visao geral",
            "2. Use crm_get_neglected_contacts() para identificar quem precisa de atencao",
            "3. Para analises individuais, use crm_score_contact(contact_id)",
            "4. Use crm_get_contact_details(contact_id) para entender o historico",
            "5. Use crm_get_follow_ups() para verificar pendencias",
            "",
            "# Formato de Resposta",
            "- Seja direto e acionavel nas recomendacoes",
            "- Use indicadores visuais: score alto (verde), medio (amarelo), baixo (vermelho)",
            "- Priorize os relacionamentos mais importantes do perfil do usuario",
            "- Sempre sugira uma acao concreta para cada alerta",
            "- Apresente os dados em formato de tabela quando possivel",
            "",
            "# Regras",
            "- SEMPRE use as ferramentas disponiveis antes de responder",
            "- Nunca invente dados - use apenas os dados reais do CRM",
            "- Seja honesto sobre relacionamentos que estao em risco",
            "- Considere o perfil do usuario ao priorizar recomendacoes",
        ],
        tools=[
            crm_score_all_relationships,
            crm_score_contact,
            crm_get_neglected_contacts,
            crm_list_all_contacts,
            crm_get_contact_details,
            crm_get_recent_activity,
            crm_get_follow_ups,
            crm_get_stats,
        ],
        markdown=True,
        show_tool_calls=True,
    )

    logger.info(f"Agente '{agent.name}' criado")
    return agent
