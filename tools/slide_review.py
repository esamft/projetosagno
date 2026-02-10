"""
Tools para o Agente Revisor de Qualidade

Fornece ferramentas de analise de qualidade, consistencia,
fluxo narrativo e aderencia a boas praticas de apresentacao.
"""
import json
from typing import Dict, Any, List
from loguru import logger


def review_presentation_quality(presentation_json: str) -> str:
    """
    Revisa a qualidade geral da apresentacao com checklist completo.

    Use esta ferramenta para fazer a revisao final de qualidade
    da apresentacao, verificando boas praticas e potenciais problemas.

    Args:
        presentation_json: JSON string com a apresentacao completa (slides, conteudo, design)

    Returns:
        JSON string com relatorio de qualidade detalhado e score
    """
    try:
        data = json.loads(presentation_json)

        slides = data.get("slides", [])
        total_slides = len(slides)

        issues = []
        warnings = []
        score = 100

        # 1. Verifica quantidade de slides
        duration = data.get("duracao_minutos", 0)
        if duration > 0:
            ratio = total_slides / duration
            if ratio > 1.5:
                issues.append({
                    "tipo": "quantidade_slides",
                    "severidade": "alta",
                    "mensagem": f"Muitos slides ({total_slides}) para {duration} minutos. Ideal: {int(duration * 0.7)} slides",
                })
                score -= 15
            elif ratio < 0.3:
                warnings.append({
                    "tipo": "quantidade_slides",
                    "severidade": "media",
                    "mensagem": f"Poucos slides ({total_slides}) para {duration} minutos. Pode ficar monotono",
                })
                score -= 5

        # 2. Verifica cada slide
        for i, slide in enumerate(slides):
            slide_num = slide.get("numero", i + 1)

            # Verifica titulo
            titulo = slide.get("titulo", "")
            if not titulo:
                warnings.append({
                    "tipo": "titulo_ausente",
                    "slide": slide_num,
                    "severidade": "media",
                    "mensagem": f"Slide {slide_num} sem titulo definido",
                })
                score -= 3

            # Verifica conteudo excessivo
            conteudo = slide.get("conteudo", "")
            if isinstance(conteudo, str):
                words = len(conteudo.split())
            elif isinstance(conteudo, list):
                words = sum(len(str(item).split()) for item in conteudo)
            else:
                words = 0

            if words > 80:
                issues.append({
                    "tipo": "conteudo_excessivo",
                    "slide": slide_num,
                    "severidade": "alta",
                    "mensagem": f"Slide {slide_num} tem ~{words} palavras. Maximo recomendado: 40",
                })
                score -= 5
            elif words > 40:
                warnings.append({
                    "tipo": "conteudo_denso",
                    "slide": slide_num,
                    "severidade": "baixa",
                    "mensagem": f"Slide {slide_num} tem ~{words} palavras. Considere simplificar",
                })
                score -= 2

            # Verifica bullet points
            bullets = slide.get("bullet_points", [])
            if len(bullets) > 6:
                issues.append({
                    "tipo": "bullets_excessivos",
                    "slide": slide_num,
                    "severidade": "alta",
                    "mensagem": f"Slide {slide_num} tem {len(bullets)} bullets. Maximo: 6",
                })
                score -= 5

        # 3. Verifica estrutura geral
        has_opening = any(
            s.get("tipo", "") in ["titulo_impacto", "secao_titulo"]
            for s in slides[:2]
        )
        has_closing = any(
            s.get("tipo", "") in ["call_to_action", "resumo"]
            for s in slides[-2:]
        )

        if not has_opening:
            warnings.append({
                "tipo": "abertura",
                "severidade": "media",
                "mensagem": "Nao foi identificado um slide de abertura forte",
            })
            score -= 5

        if not has_closing:
            warnings.append({
                "tipo": "fechamento",
                "severidade": "media",
                "mensagem": "Nao foi identificado um slide de fechamento/CTA",
            })
            score -= 5

        # Classificacao final
        score = max(0, min(100, score))
        if score >= 85:
            classification = "Excelente"
            verdict = "Apresentacao bem estruturada e pronta"
        elif score >= 70:
            classification = "Boa"
            verdict = "Pequenos ajustes recomendados"
        elif score >= 50:
            classification = "Regular"
            verdict = "Necessita revisoes antes de apresentar"
        else:
            classification = "Precisa de trabalho"
            verdict = "Revisao significativa necessaria"

        report = {
            "status": "success",
            "relatorio_qualidade": {
                "score": score,
                "classificacao": classification,
                "veredicto": verdict,
                "total_slides": total_slides,
                "problemas_criticos": len(issues),
                "avisos": len(warnings),
            },
            "problemas": issues,
            "avisos": warnings,
            "checklist_final": [
                {"item": "Slide de abertura impactante", "status": "ok" if has_opening else "pendente"},
                {"item": "Slide de fechamento/CTA", "status": "ok" if has_closing else "pendente"},
                {"item": "Maximo 6 bullets por slide", "status": "ok" if not any(i["tipo"] == "bullets_excessivos" for i in issues) else "falha"},
                {"item": "Conteudo conciso por slide", "status": "ok" if not any(i["tipo"] == "conteudo_excessivo" for i in issues) else "falha"},
                {"item": "Todos os slides com titulo", "status": "ok" if not any(w["tipo"] == "titulo_ausente" for w in warnings) else "pendente"},
            ],
        }

        logger.info(f"Revisao concluida: score={score}, classificacao={classification}")
        return json.dumps(report, ensure_ascii=False, indent=2)

    except json.JSONDecodeError:
        return json.dumps({
            "status": "error",
            "message": "JSON invalido fornecido"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro na revisao: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def check_flow_consistency(slides_json: str) -> str:
    """
    Verifica a consistencia do fluxo narrativo entre slides.

    Use esta ferramenta para analisar se a sequencia de slides
    faz sentido narrativo e se as transicoes sao naturais.

    Args:
        slides_json: JSON string com a lista de slides e seus tipos/secoes

    Returns:
        JSON string com analise de fluxo e sugestoes de melhoria
    """
    try:
        data = json.loads(slides_json)
        slides = data.get("slides", [])

        flow_issues = []
        transitions = []

        for i in range(len(slides) - 1):
            current = slides[i]
            next_slide = slides[i + 1]

            current_section = current.get("secao", "")
            next_section = next_slide.get("secao", "")
            current_type = current.get("tipo", "")
            next_type = next_slide.get("tipo", "")

            # Verifica mudanca de secao
            if current_section != next_section:
                transitions.append({
                    "de_slide": current.get("numero", i + 1),
                    "para_slide": next_slide.get("numero", i + 2),
                    "de_secao": current_section,
                    "para_secao": next_section,
                    "sugestao_transicao": _suggest_transition(current_section, next_section),
                })

            # Detecta problemas de fluxo
            if current_type == "call_to_action" and next_type not in ["resumo", "secao_titulo", ""]:
                flow_issues.append({
                    "slides": [current.get("numero", i + 1), next_slide.get("numero", i + 2)],
                    "problema": "CTA seguido de conteudo adicional pode diluir a acao",
                    "sugestao": "Mova o CTA para mais perto do final",
                })

            if current_type == "dados_graficos" and next_type == "dados_graficos":
                if i > 0 and slides[i - 1].get("tipo") == "dados_graficos":
                    flow_issues.append({
                        "slides": [i, i + 1, i + 2],
                        "problema": "3+ slides consecutivos de dados pode cansar a audiencia",
                        "sugestao": "Intercale com um slide de insight ou historia",
                    })

        # Analisa distribuicao de tipos
        type_counts = {}
        for s in slides:
            t = s.get("tipo", "conteudo_padrao")
            type_counts[t] = type_counts.get(t, 0) + 1

        variety_score = min(100, len(type_counts) * 15)

        analysis = {
            "status": "success",
            "analise_fluxo": {
                "total_slides": len(slides),
                "total_transicoes_secao": len(transitions),
                "problemas_fluxo": len(flow_issues),
                "variedade_visual": {
                    "score": variety_score,
                    "tipos_usados": len(type_counts),
                    "distribuicao": type_counts,
                },
            },
            "transicoes": transitions,
            "problemas": flow_issues,
            "sugestoes_gerais": [
                "Varie os tipos de slide para manter engajamento visual",
                "Cada transicao de secao deve ter uma frase de conexao",
                "Mantenha um ritmo: informacao densa seguida de pausa visual",
                "O publico lembra melhor o inicio e o fim - use-os estrategicamente",
            ]
        }

        logger.info(f"Analise de fluxo: {len(transitions)} transicoes, {len(flow_issues)} problemas")
        return json.dumps(analysis, ensure_ascii=False, indent=2)

    except json.JSONDecodeError:
        return json.dumps({
            "status": "error",
            "message": "JSON invalido fornecido"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro na analise de fluxo: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def _suggest_transition(from_section: str, to_section: str) -> str:
    """Sugere uma frase de transicao entre secoes."""
    transitions = {
        ("Abertura", "Problema"): "Agora que temos o contexto, vamos ao desafio que enfrentamos...",
        ("Problema", "Solucao"): "A boa noticia e que existe uma solucao...",
        ("Solucao", "Prova Social"): "E nao somos so nos que dizemos isso. Veja os resultados...",
        ("Prova Social", "Proposta"): "Com isso em mente, aqui esta nossa proposta...",
        ("Proposta", "Call to Action"): "Entao, qual o proximo passo?",
        ("Introducao", "Fundamentos"): "Antes de avancar, vamos estabelecer as bases...",
        ("Fundamentos", "Desenvolvimento"): "Com essa base, vamos aprofundar...",
        ("Desenvolvimento", "Aplicacao Pratica"): "Agora vamos ver isso na pratica...",
        ("Aplicacao Pratica", "Resumo e Proximos Passos"): "Para finalizar, vamos recapitular...",
        ("Resumo Executivo", "Metricas e Dados"): "Vamos aos numeros em detalhe...",
        ("Metricas e Dados", "Analise e Insights"): "O que esses numeros nos dizem?",
        ("Analise e Insights", "Desafios e Riscos"): "Mas tambem precisamos falar sobre os desafios...",
        ("Desafios e Riscos", "Proximos Passos"): "Para superar esses desafios, nosso plano e...",
    }

    return transitions.get(
        (from_section, to_section),
        f"Transicao de '{from_section}' para '{to_section}' - crie uma frase de conexao natural"
    )
