"""
Agente Orquestrador do CRM de Relacionamentos

Agente principal que coordena todos os agentes especializados
usando o sistema de Teams do Agno Framework.
Pode delegar tarefas para o agente mais adequado.
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from loguru import logger

from config.settings import DEFAULT_MODEL
from config.crm_profiles import get_agent_instructions
from storage.crm_store import load_profile

from agents.relationship_analyst import create_relationship_analyst
from agents.communication_strategist import create_communication_strategist
from agents.network_mapper import create_network_mapper
from agents.priority_advisor import create_priority_advisor


def create_crm_orchestrator() -> Agent:
    """
    Cria o Orquestrador do CRM que coordena todos os agentes especializados.

    O orquestrador atua como ponto de entrada principal, entendendo
    a intencao do usuario e delegando para o agente especializado
    mais adequado. Tambem pode combinar resultados de multiplos agentes.

    Agentes disponveis:
    - Analista de Relacionamentos: scores, saude, tendencias
    - Estrategista de Comunicacao: sugestoes, planos, registro de interacoes
    - Mapeador de Rede: estrutura, clusters, gaps, diversidade
    - Consultor de Prioridades: priorizacao, gestao completa, setup

    Returns:
        Agent orquestrador configurado com team de agentes
    """
    profile = load_profile()
    tipo = profile.get("tipo", "custom") if profile else "custom"
    instrucoes_perfil = get_agent_instructions(tipo)

    # Criar agentes especializados
    analyst = create_relationship_analyst()
    strategist = create_communication_strategist()
    mapper = create_network_mapper()
    advisor = create_priority_advisor()

    orchestrator = Agent(
        name="CRM de Relacionamentos - Orquestrador",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Orquestrador principal do CRM que coordena agentes especializados "
            "para manter seus relacionamentos saudaveis e estrategicos"
        ),
        instructions=[
            "# Role",
            "Voce e o Orquestrador do CRM de Relacionamentos Pessoal. Seu trabalho "
            "e entender o que o usuario precisa e coordenar os agentes especializados "
            "para entregar a melhor resposta possivel.",
            "",
            "# Contexto do Perfil",
            instrucoes_perfil,
            "",
            "# Agentes Disponiveis no Seu Time",
            "",
            "## 1. Analista de Relacionamentos",
            "- Quando usar: analise de saude, scores, tendencias, alertas",
            "- Exemplos: 'como estao meus relacionamentos?', 'quem estou negligenciando?'",
            "",
            "## 2. Estrategista de Comunicacao",
            "- Quando usar: sugestoes de contato, planos de comunicacao, registrar interacoes",
            "- Exemplos: 'com quem devo falar hoje?', 'registre que almocei com João'",
            "",
            "## 3. Mapeador de Rede",
            "- Quando usar: analise da estrutura da rede, clusters, gaps",
            "- Exemplos: 'como esta minha rede?', 'onde tenho gaps?'",
            "",
            "## 4. Consultor de Prioridades",
            "- Quando usar: priorizacao, gestao do CRM, setup, perguntas gerais",
            "- Exemplos: 'adicione contato', 'configure meu perfil', 'o que devo priorizar?'",
            "",
            "# Como Orquestrar",
            "1. Entenda a intencao do usuario",
            "2. Delegue para o agente mais adequado usando transfer_to_<agente>",
            "3. Se a pergunta envolve multiplos aspectos, delegue para o mais relevante",
            "4. Para gestao do CRM (CRUD), sempre delegue para o Consultor de Prioridades",
            "5. Para primeira interacao ou setup, delegue para o Consultor de Prioridades",
            "",
            "# Boas-vindas",
            "Na primeira interacao, apresente-se brevemente e pergunte como pode ajudar.",
            "Se o perfil nao estiver configurado, sugira configurar primeiro.",
            "",
            "# Tom de Voz",
            "- Profissional mas acessivel",
            "- Direto e acionavel",
            "- Adaptado ao perfil do usuario",
            "- Em portugues brasileiro",
        ],
        team=[analyst, strategist, mapper, advisor],
        markdown=True,
        show_tool_calls=True,
    )

    logger.info("Orquestrador CRM criado com time de 4 agentes especializados")
    return orchestrator
