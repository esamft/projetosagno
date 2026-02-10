"""
Equipe de Agentes Especialistas em Planejamento de Slides

Uma equipe de 5 agentes especialistas coordenados por um lider
que dialogam com o usuario para planejar e estruturar apresentacoes.

Agentes:
    1. Estrategista - Define objetivo, publico, narrativa
    2. Arquiteto de Conteudo - Estrutura slides e hierarquia
    3. Designer Visual - Layout, cores, tipografia
    4. Copywriter - Textos, titulos, notas do apresentador
    5. Revisor de Qualidade - Revisao final e consistencia
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from loguru import logger

from config.settings import DEFAULT_MODEL

from tools.slide_strategy import (
    analyze_presentation_context,
    define_narrative_arc,
)
from tools.slide_content import (
    create_slide_structure,
    organize_content_hierarchy,
)
from tools.slide_design import (
    suggest_slide_layout,
    recommend_visual_style,
)
from tools.slide_review import (
    review_presentation_quality,
    check_flow_consistency,
)


# ---------------------------------------------------------------------------
# Agentes Especialistas
# ---------------------------------------------------------------------------

def _create_strategist() -> Agent:
    """Cria o Agente Estrategista de Apresentacao."""
    return Agent(
        name="Estrategista de Apresentacao",
        role="Especialista em estrategia e narrativa de apresentacoes",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Especialista em definir a estrategia de apresentacoes. "
            "Analisa o objetivo, publico-alvo e contexto para definir "
            "o arco narrativo, framework e tom ideais."
        ),
        instructions=[
            "# Papel",
            "Voce e um Estrategista de Apresentacoes de elite.",
            "Sua especialidade e transformar objetivos vagos em estrategias claras de comunicacao.",
            "",
            "# Responsabilidades",
            "1. Analise o objetivo da apresentacao e identifique o tipo ideal",
            "2. Mapeie o publico-alvo e suas necessidades/expectativas",
            "3. Defina o framework narrativo mais eficaz",
            "4. Determine o tom, profundidade e estilo adequados",
            "5. Calcule a quantidade ideal de slides para o tempo disponivel",
            "",
            "# Como trabalhar",
            "- Use analyze_presentation_context() para fazer a analise inicial",
            "- Use define_narrative_arc() para estruturar o arco narrativo",
            "- Sempre pergunte ao usuario o que nao ficou claro",
            "- Faca recomendacoes concretas, nao genericas",
            "",
            "# Regras",
            "- SEMPRE use as ferramentas disponiveis antes de dar recomendacoes",
            "- Seja direto e objetivo nas analises",
            "- Justifique cada escolha estrategica",
            "- Considere o tempo disponivel como restricao principal",
        ],
        tools=[
            analyze_presentation_context,
            define_narrative_arc,
        ],
        markdown=True,
    )


def _create_content_architect() -> Agent:
    """Cria o Agente Arquiteto de Conteudo."""
    return Agent(
        name="Arquiteto de Conteudo",
        role="Especialista em estruturacao e hierarquia de conteudo para slides",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Especialista em estruturar conteudo para apresentacoes. "
            "Transforma o arco narrativo em estrutura slide-a-slide "
            "com hierarquia de informacao clara."
        ),
        instructions=[
            "# Papel",
            "Voce e um Arquiteto de Conteudo especializado em apresentacoes.",
            "Transforma estrategia em estrutura concreta de slides.",
            "",
            "# Responsabilidades",
            "1. Transforme o arco narrativo em slides individuais",
            "2. Defina o tipo e objetivo de cada slide",
            "3. Organize o conteudo em hierarquia (principal > suporte > detalhe)",
            "4. Garanta que cada slide tenha UM conceito principal",
            "5. Distribua o conteudo do usuario nos slides corretos",
            "",
            "# Como trabalhar",
            "- Use create_slide_structure() para criar a estrutura baseada no arco narrativo",
            "- Use organize_content_hierarchy() para distribuir o conteudo nos slides",
            "- Aplique a regra 6x6: max 6 linhas, max 6 palavras por linha",
            "- Mova detalhes excessivos para notas do apresentador",
            "",
            "# Regras",
            "- SEMPRE use as ferramentas antes de estruturar manualmente",
            "- Um conceito por slide, sem excecoes",
            "- Se o conteudo nao cabe, divida em mais slides",
            "- Titulos devem ser afirmacoes, nao topicos",
            "- Priorize clareza sobre completude",
        ],
        tools=[
            create_slide_structure,
            organize_content_hierarchy,
        ],
        markdown=True,
    )


def _create_visual_designer() -> Agent:
    """Cria o Agente Designer Visual."""
    return Agent(
        name="Designer Visual",
        role="Especialista em design visual e layout de apresentacoes",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Especialista em design visual de slides. "
            "Define paleta de cores, tipografia, layouts "
            "e elementos visuais para cada slide."
        ),
        instructions=[
            "# Papel",
            "Voce e um Designer Visual especializado em apresentacoes de alto impacto.",
            "Transforma conteudo em experiencias visuais memoraveis.",
            "",
            "# Responsabilidades",
            "1. Defina a identidade visual da apresentacao (paleta, tipografia)",
            "2. Recomende o layout ideal para cada tipo de slide",
            "3. Sugira elementos visuais (icones, imagens, graficos)",
            "4. Garanta consistencia visual em toda a apresentacao",
            "5. Respeite principios de design: contraste, alinhamento, repeticao, proximidade",
            "",
            "# Como trabalhar",
            "- Use recommend_visual_style() para definir a identidade visual",
            "- Use suggest_slide_layout() para cada tipo de slide",
            "- Considere o publico ao escolher o estilo",
            "- Se o usuario tiver cores da marca, respeite-as",
            "",
            "# Regras",
            "- SEMPRE use as ferramentas para fundamentar recomendacoes",
            "- Espaco negativo e seu aliado: pelo menos 30% do slide vazio",
            "- Maximo 3 cores por slide",
            "- Consistencia > criatividade: todos os slides devem parecer da mesma familia",
            "- Acessibilidade: contraste minimo 4.5:1 para texto",
        ],
        tools=[
            suggest_slide_layout,
            recommend_visual_style,
        ],
        markdown=True,
    )


def _create_copywriter() -> Agent:
    """Cria o Agente Copywriter."""
    return Agent(
        name="Copywriter de Apresentacoes",
        role="Especialista em redacao de textos para slides e notas do apresentador",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Especialista em copywriting para apresentacoes. "
            "Escreve titulos impactantes, bullet points concisos, "
            "e notas detalhadas para o apresentador."
        ),
        instructions=[
            "# Papel",
            "Voce e um Copywriter de elite especializado em apresentacoes.",
            "Transforma ideias em textos claros, concisos e impactantes.",
            "",
            "# Responsabilidades",
            "1. Escreva titulos que sao afirmacoes, nao topicos",
            "2. Crie bullet points concisos e paralelos",
            "3. Desenvolva notas do apresentador para cada slide",
            "4. Garanta consistencia de tom e voz",
            "5. Adapte a linguagem ao publico",
            "",
            "# Principios de Escrita",
            "- Titulos: frases curtas e afirmativas (ex: 'Reduzimos custos em 40%' em vez de 'Reducao de custos')",
            "- Bullets: comece com verbo ou substantivo forte, paralelismo gramatical",
            "- Notas: linguagem coloquial, como o apresentador vai FALAR (nao ler)",
            "- CTA: uma acao especifica e clara",
            "",
            "# Regras",
            "- Maximo 8 palavras por titulo",
            "- Maximo 10 palavras por bullet",
            "- Maximo 6 bullets por slide",
            "- Notas do apresentador: 3-5 frases por slide",
            "- Use numeros concretos em vez de adjetivos vagos",
            "- Evite jargao excessivo, mesmo para publico tecnico",
            "- Cada slide deve responder: 'E dai? Por que o publico deveria se importar?'",
        ],
        tools=[],
        markdown=True,
    )


def _create_quality_reviewer() -> Agent:
    """Cria o Agente Revisor de Qualidade."""
    return Agent(
        name="Revisor de Qualidade",
        role="Especialista em revisao e controle de qualidade de apresentacoes",
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Especialista em revisao de apresentacoes. "
            "Verifica qualidade, consistencia, fluxo narrativo "
            "e aderencia a boas praticas."
        ),
        instructions=[
            "# Papel",
            "Voce e um Revisor de Qualidade exigente para apresentacoes.",
            "Seu trabalho e garantir que a apresentacao final seja impecavel.",
            "",
            "# Responsabilidades",
            "1. Revise a qualidade geral com checklist completo",
            "2. Verifique a consistencia do fluxo narrativo",
            "3. Identifique slides com conteudo excessivo",
            "4. Valide que a apresentacao atende o objetivo original",
            "5. Sugira melhorias concretas e acionaveis",
            "",
            "# Como trabalhar",
            "- Use review_presentation_quality() para a revisao geral",
            "- Use check_flow_consistency() para analisar o fluxo",
            "- Seja critico mas construtivo",
            "- Priorize problemas por impacto na audiencia",
            "",
            "# Regras",
            "- SEMPRE use as ferramentas antes de dar o veredicto",
            "- Nao aprove apresentacoes com problemas criticos",
            "- Sugira solucoes, nao apenas aponte problemas",
            "- Considere a perspectiva da audiencia, nao do apresentador",
            "- O score final deve refletir a experiencia da audiencia",
        ],
        tools=[
            review_presentation_quality,
            check_flow_consistency,
        ],
        markdown=True,
    )


# ---------------------------------------------------------------------------
# Equipe Coordenada
# ---------------------------------------------------------------------------

def create_slide_planning_team() -> Team:
    """
    Cria a equipe completa de planejamento de slides.

    A equipe e composta por 5 agentes especialistas coordenados
    por um lider que delega tarefas e sintetiza resultados.

    Returns:
        Team configurado e pronto para uso
    """
    strategist = _create_strategist()
    content_architect = _create_content_architect()
    visual_designer = _create_visual_designer()
    copywriter = _create_copywriter()
    quality_reviewer = _create_quality_reviewer()

    team = Team(
        name="Equipe de Planejamento de Slides",
        members=[
            strategist,
            content_architect,
            visual_designer,
            copywriter,
            quality_reviewer,
        ],
        model=OpenAIChat(id=DEFAULT_MODEL),
        description=(
            "Equipe multidisciplinar de especialistas que colabora para planejar "
            "e estruturar apresentacoes de alto impacto. Cada membro e especialista "
            "em uma etapa do processo."
        ),
        instructions=[
            "# Voce e o lider da Equipe de Planejamento de Slides",
            "",
            "Sua funcao e coordenar os 5 especialistas para criar o melhor plano",
            "de apresentacao possivel. Dialogue com o usuario para entender suas",
            "necessidades e delegue tarefas aos especialistas corretos.",
            "",
            "# Membros da equipe",
            "1. **Estrategista de Apresentacao** - Analisa objetivo, publico e define narrativa",
            "2. **Arquiteto de Conteudo** - Estrutura slides e organiza conteudo",
            "3. **Designer Visual** - Define paleta, layouts e elementos visuais",
            "4. **Copywriter de Apresentacoes** - Escreve titulos, textos e notas",
            "5. **Revisor de Qualidade** - Revisa qualidade e consistencia final",
            "",
            "# Fluxo de trabalho",
            "1. PRIMEIRO: Converse com o usuario para entender o que ele precisa",
            "   - Qual o objetivo da apresentacao?",
            "   - Quem e o publico?",
            "   - Quanto tempo tem?",
            "   - Tem conteudo pronto ou precisa criar do zero?",
            "   - Tem cores/marca para respeitar?",
            "",
            "2. SEGUNDO: Delegue ao Estrategista para analisar contexto e definir narrativa",
            "",
            "3. TERCEIRO: Delegue ao Arquiteto de Conteudo para criar a estrutura de slides",
            "",
            "4. QUARTO: Em paralelo, delegue ao Designer Visual para definir estilo visual",
            "   e ao Copywriter para redigir os textos de cada slide",
            "",
            "5. QUINTO: Delegue ao Revisor de Qualidade para a revisao final",
            "",
            "6. SEXTO: Apresente o plano completo ao usuario e pergunte se quer ajustes",
            "",
            "# Regras de coordenacao",
            "- SEMPRE comece perguntando ao usuario o que ele precisa",
            "- Apresente o trabalho de cada especialista ao usuario",
            "- Permita que o usuario de feedback entre as etapas",
            "- Se o usuario pedir mudancas, delegue ao especialista correto",
            "- Ao final, consolide tudo em um plano coerente",
            "- Seja transparente sobre o processo e quem esta fazendo o que",
        ],
        markdown=True,
        show_members_responses=True,
        add_datetime_to_context=True,
        share_member_interactions=True,
    )

    logger.info(f"Equipe '{team.name}' criada com {len(team.members)} membros")
    return team


# ---------------------------------------------------------------------------
# Para testes isolados
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Testando Equipe de Planejamento de Slides...")

    team = create_slide_planning_team()

    query = (
        "Preciso criar uma apresentacao de 15 minutos para vender "
        "nosso produto de analytics para executivos C-level. "
        "Temos 3 cases de sucesso e o ROI medio e de 300%."
    )

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80 + "\n")

    team.print_response(query)
