"""
Tools para o Agente Estrategista de Apresentacao

Fornece frameworks de analise de contexto, definicao de publico-alvo,
e estruturacao de arco narrativo para apresentacoes.
"""
import json
from typing import Optional
from loguru import logger


def analyze_presentation_context(
    objective: str,
    audience: str,
    duration_minutes: int,
    context: Optional[str] = None
) -> str:
    """
    Analisa o contexto da apresentacao e gera recomendacoes estrategicas.

    Use esta ferramenta para analisar o objetivo, publico e contexto
    da apresentacao antes de definir a estrategia.

    Args:
        objective: Objetivo principal da apresentacao (ex: "Vender produto X", "Ensinar conceito Y")
        audience: Descricao do publico-alvo (ex: "Executivos C-level", "Estudantes universitarios")
        duration_minutes: Duracao estimada em minutos
        context: Contexto adicional (ex: "Evento corporativo", "Aula online")

    Returns:
        JSON string com analise estrategica completa
    """
    try:
        # Calcula slides recomendados (regra: ~1-2 min por slide)
        slides_min = max(3, duration_minutes // 2)
        slides_max = max(5, duration_minutes)
        slides_ideal = max(4, int(duration_minutes * 0.7))

        # Determina tom baseado no publico
        audience_lower = audience.lower()
        if any(w in audience_lower for w in ["c-level", "executivo", "diretor", "investidor", "board"]):
            tone = "Executivo e direto"
            depth = "Alto nivel, foco em resultados e ROI"
            visual_style = "Minimalista e profissional"
        elif any(w in audience_lower for w in ["tecnico", "engenheiro", "desenvolvedor", "programador"]):
            tone = "Tecnico e detalhado"
            depth = "Profundo, com dados e evidencias"
            visual_style = "Diagramas e fluxos tecnicos"
        elif any(w in audience_lower for w in ["estudante", "aluno", "universitario", "academico"]):
            tone = "Didatico e engajante"
            depth = "Progressivo, do basico ao avancado"
            visual_style = "Visual e interativo"
        elif any(w in audience_lower for w in ["vendas", "comercial", "cliente", "prospect"]):
            tone = "Persuasivo e impactante"
            depth = "Beneficios e casos de sucesso"
            visual_style = "Impactante com provas sociais"
        else:
            tone = "Profissional e acessivel"
            depth = "Equilibrado entre conceitos e pratica"
            visual_style = "Limpo e organizado"

        # Determina tipo de apresentacao
        objective_lower = objective.lower()
        if any(w in objective_lower for w in ["vender", "pitch", "investimento", "proposta"]):
            presentation_type = "Pitch/Venda"
            framework = "Problema -> Solucao -> Beneficios -> Prova -> CTA"
        elif any(w in objective_lower for w in ["ensinar", "treinar", "capacitar", "aula"]):
            presentation_type = "Educacional"
            framework = "Contexto -> Conceitos -> Exemplos -> Pratica -> Resumo"
        elif any(w in objective_lower for w in ["relatorio", "resultado", "metricas", "performance"]):
            presentation_type = "Relatorio"
            framework = "Resumo Executivo -> Dados -> Analise -> Insights -> Proximos Passos"
        elif any(w in objective_lower for w in ["projeto", "plano", "roadmap", "estrategia"]):
            presentation_type = "Planejamento"
            framework = "Visao -> Situacao Atual -> Estrategia -> Cronograma -> Recursos"
        elif any(w in objective_lower for w in ["inspirar", "motivar", "keynote", "palestra"]):
            presentation_type = "Keynote/Inspiracional"
            framework = "Gancho -> Historia -> Insight -> Evidencia -> Chamada a Acao"
        else:
            presentation_type = "Informativa"
            framework = "Introducao -> Contexto -> Desenvolvimento -> Conclusao -> Q&A"

        analysis = {
            "status": "success",
            "analise_estrategica": {
                "tipo_apresentacao": presentation_type,
                "framework_narrativo": framework,
                "tom_recomendado": tone,
                "profundidade": depth,
                "estilo_visual": visual_style,
            },
            "parametros_slides": {
                "duracao_minutos": duration_minutes,
                "slides_minimo": slides_min,
                "slides_maximo": slides_max,
                "slides_ideal": slides_ideal,
                "tempo_medio_por_slide": f"{duration_minutes / slides_ideal:.1f} minutos",
            },
            "publico": {
                "descricao": audience,
                "contexto": context or "Nao especificado",
            },
            "recomendacoes": [
                f"Use o framework: {framework}",
                f"Mantenha o tom {tone.lower()} ao longo de toda a apresentacao",
                f"Prepare {slides_ideal} slides para {duration_minutes} minutos",
                f"Estilo visual recomendado: {visual_style}",
                "Inclua um slide de abertura impactante e um fechamento memoravel",
            ]
        }

        logger.info(f"Analise estrategica concluida: tipo={presentation_type}")
        return json.dumps(analysis, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro na analise estrategica: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def define_narrative_arc(
    presentation_type: str,
    key_messages: str,
    num_slides: int
) -> str:
    """
    Define o arco narrativo da apresentacao com estrutura de secoes.

    Use esta ferramenta apos a analise de contexto para criar
    a estrutura narrativa detalhada da apresentacao.

    Args:
        presentation_type: Tipo da apresentacao (ex: "Pitch/Venda", "Educacional", "Relatorio")
        key_messages: Mensagens-chave separadas por ponto-e-virgula (ex: "Nosso produto resolve X; Temos Y clientes; ROI de Z%")
        num_slides: Numero total de slides planejados

    Returns:
        JSON string com arco narrativo detalhado
    """
    try:
        messages = [m.strip() for m in key_messages.split(";") if m.strip()]

        # Define estrutura de secoes baseada no tipo
        sections = {
            "Pitch/Venda": [
                {"nome": "Abertura", "peso": 0.10, "objetivo": "Capturar atencao com o problema"},
                {"nome": "Problema", "peso": 0.15, "objetivo": "Aprofundar a dor do publico"},
                {"nome": "Solucao", "peso": 0.25, "objetivo": "Apresentar a solucao com clareza"},
                {"nome": "Prova Social", "peso": 0.20, "objetivo": "Demonstrar resultados e credibilidade"},
                {"nome": "Proposta", "peso": 0.15, "objetivo": "Detalhar oferta e diferenciais"},
                {"nome": "Call to Action", "peso": 0.15, "objetivo": "Fechar com acao clara"},
            ],
            "Educacional": [
                {"nome": "Introducao", "peso": 0.10, "objetivo": "Contextualizar e motivar o aprendizado"},
                {"nome": "Fundamentos", "peso": 0.20, "objetivo": "Estabelecer base conceitual"},
                {"nome": "Desenvolvimento", "peso": 0.35, "objetivo": "Aprofundar com exemplos e detalhes"},
                {"nome": "Aplicacao Pratica", "peso": 0.20, "objetivo": "Demonstrar uso real"},
                {"nome": "Resumo e Proximos Passos", "peso": 0.15, "objetivo": "Consolidar aprendizado"},
            ],
            "Relatorio": [
                {"nome": "Resumo Executivo", "peso": 0.15, "objetivo": "Visao geral dos resultados"},
                {"nome": "Metricas e Dados", "peso": 0.30, "objetivo": "Apresentar numeros com contexto"},
                {"nome": "Analise e Insights", "peso": 0.25, "objetivo": "Interpretar os dados"},
                {"nome": "Desafios e Riscos", "peso": 0.15, "objetivo": "Transparencia sobre obstaculos"},
                {"nome": "Proximos Passos", "peso": 0.15, "objetivo": "Plano de acao"},
            ],
            "Planejamento": [
                {"nome": "Visao e Contexto", "peso": 0.15, "objetivo": "Estabelecer o porque"},
                {"nome": "Situacao Atual", "peso": 0.15, "objetivo": "Diagnostico honesto"},
                {"nome": "Estrategia", "peso": 0.25, "objetivo": "O que sera feito e como"},
                {"nome": "Cronograma", "peso": 0.20, "objetivo": "Timeline com marcos"},
                {"nome": "Recursos e Investimento", "peso": 0.15, "objetivo": "O que e necessario"},
                {"nome": "Resultados Esperados", "peso": 0.10, "objetivo": "Metas e KPIs"},
            ],
            "Keynote/Inspiracional": [
                {"nome": "Gancho", "peso": 0.10, "objetivo": "Abrir com historia ou dado impactante"},
                {"nome": "Jornada/Historia", "peso": 0.25, "objetivo": "Construir narrativa envolvente"},
                {"nome": "Insight Central", "peso": 0.20, "objetivo": "Revelar a mensagem principal"},
                {"nome": "Evidencias", "peso": 0.20, "objetivo": "Sustentar com dados e exemplos"},
                {"nome": "Transformacao", "peso": 0.15, "objetivo": "Mostrar o impacto possivel"},
                {"nome": "Chamada a Acao", "peso": 0.10, "objetivo": "Inspirar acao concreta"},
            ],
        }

        # Fallback para tipo generico
        selected_sections = sections.get(presentation_type, [
            {"nome": "Introducao", "peso": 0.15, "objetivo": "Contextualizar o tema"},
            {"nome": "Desenvolvimento", "peso": 0.50, "objetivo": "Conteudo principal"},
            {"nome": "Conclusao", "peso": 0.20, "objetivo": "Sintetizar e concluir"},
            {"nome": "Q&A", "peso": 0.15, "objetivo": "Espaco para perguntas"},
        ])

        # Distribui slides pelas secoes
        slides_distribuidos = []
        slides_restantes = num_slides
        for i, section in enumerate(selected_sections):
            if i == len(selected_sections) - 1:
                n_slides = slides_restantes
            else:
                n_slides = max(1, round(num_slides * section["peso"]))
                slides_restantes -= n_slides

            slides_distribuidos.append({
                "secao": section["nome"],
                "num_slides": max(1, n_slides),
                "objetivo": section["objetivo"],
                "mensagens_sugeridas": [m for m in messages if i == 0] if i == 0 else [],
            })

        # Distribui mensagens-chave pelas secoes relevantes
        if messages:
            msg_per_section = max(1, len(messages) // max(1, len(slides_distribuidos) - 2))
            for i, section in enumerate(slides_distribuidos):
                start = i * msg_per_section
                end = start + msg_per_section
                section["mensagens_sugeridas"] = messages[start:end]

        narrative = {
            "status": "success",
            "arco_narrativo": {
                "tipo": presentation_type,
                "total_slides": num_slides,
                "total_secoes": len(slides_distribuidos),
                "secoes": slides_distribuidos,
            },
            "dicas_narrativas": [
                "Cada secao deve ter uma transicao clara para a proxima",
                "A primeira e ultima impressao sao as mais memoraveis",
                "Distribua as mensagens-chave nos momentos de maior atencao",
                "Use a regra do 3: agrupe informacoes em trios quando possivel",
            ]
        }

        logger.info(f"Arco narrativo definido: {len(slides_distribuidos)} secoes, {num_slides} slides")
        return json.dumps(narrative, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao definir arco narrativo: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)
