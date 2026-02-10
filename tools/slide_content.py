"""
Tools para o Agente Arquiteto de Conteudo

Fornece ferramentas para estruturar slides, definir hierarquia
de informacao e organizar conteudo por secao.
"""
import json
from loguru import logger


def create_slide_structure(
    narrative_json: str,
    topic: str
) -> str:
    """
    Cria a estrutura detalhada de cada slide com base no arco narrativo.

    Use esta ferramenta para transformar o arco narrativo em uma
    estrutura slide-a-slide com titulo, tipo de conteudo e objetivos.

    Args:
        narrative_json: JSON string do arco narrativo (output de define_narrative_arc)
        topic: Tema principal da apresentacao

    Returns:
        JSON string com estrutura detalhada de cada slide
    """
    try:
        data = json.loads(narrative_json)

        if data.get("status") != "success":
            return json.dumps({
                "status": "error",
                "message": "Arco narrativo invalido ou com erro"
            }, ensure_ascii=False)

        arco = data.get("arco_narrativo", {})
        secoes = arco.get("secoes", [])

        slides = []
        slide_num = 0

        for secao in secoes:
            nome_secao = secao.get("secao", "")
            objetivo = secao.get("objetivo", "")
            n_slides = secao.get("num_slides", 1)
            mensagens = secao.get("mensagens_sugeridas", [])

            for i in range(n_slides):
                slide_num += 1
                slide = {
                    "numero": slide_num,
                    "secao": nome_secao,
                    "tipo": _determine_slide_type(nome_secao, i, n_slides),
                    "objetivo": objetivo if i == 0 else f"Continuacao: {objetivo}",
                    "mensagem_chave": mensagens[i] if i < len(mensagens) else "",
                    "elementos_sugeridos": _suggest_elements(nome_secao, i, n_slides),
                    "notas": "",
                }
                slides.append(slide)

        structure = {
            "status": "success",
            "tema": topic,
            "total_slides": len(slides),
            "slides": slides,
            "regras_conteudo": [
                "Maximo 6 linhas de texto por slide",
                "Maximo 6 palavras por linha (regra 6x6)",
                "Um conceito principal por slide",
                "Use visuais para complementar, nao repetir o texto",
                "Titulos devem ser afirmacoes, nao topicos",
            ]
        }

        logger.info(f"Estrutura criada: {len(slides)} slides para '{topic}'")
        return json.dumps(structure, ensure_ascii=False, indent=2)

    except json.JSONDecodeError:
        return json.dumps({
            "status": "error",
            "message": "JSON invalido fornecido"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao criar estrutura: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def organize_content_hierarchy(
    slide_structure_json: str,
    raw_content: str
) -> str:
    """
    Organiza o conteudo bruto em hierarquia para cada slide.

    Use esta ferramenta para pegar conteudo bruto do usuario e
    distribui-lo nos slides de forma hierarquica (principal, secundario, detalhe).

    Args:
        slide_structure_json: JSON string da estrutura de slides (output de create_slide_structure)
        raw_content: Conteudo bruto/notas do usuario para distribuir nos slides

    Returns:
        JSON string com conteudo organizado hierarquicamente por slide
    """
    try:
        data = json.loads(slide_structure_json)

        if data.get("status") != "success":
            return json.dumps({
                "status": "error",
                "message": "Estrutura de slides invalida"
            }, ensure_ascii=False)

        slides = data.get("slides", [])

        # Analisa densidade do conteudo
        words = raw_content.split()
        word_count = len(words)
        words_per_slide = word_count / max(1, len(slides))

        # Classifica densidade
        if words_per_slide > 100:
            density = "alta"
            density_advice = "Conteudo denso - priorize e corte impiedosamente"
        elif words_per_slide > 40:
            density = "media"
            density_advice = "Boa quantidade - selecione o essencial para cada slide"
        else:
            density = "baixa"
            density_advice = "Conteudo enxuto - pode precisar expandir alguns pontos"

        organized = {
            "status": "success",
            "analise_conteudo": {
                "total_palavras": word_count,
                "palavras_por_slide": round(words_per_slide),
                "densidade": density,
                "recomendacao": density_advice,
            },
            "conteudo_bruto": raw_content,
            "slides": slides,
            "hierarquia_modelo": {
                "nivel_1_titulo": "Afirmacao principal do slide (maximo 8 palavras)",
                "nivel_2_pontos": "2-4 pontos de suporte (maximo 10 palavras cada)",
                "nivel_3_detalhes": "Dados, exemplos ou evidencias especificas",
                "nivel_4_notas": "Notas do apresentador (o que dizer, nao mostrar)",
            },
            "instrucoes": [
                "Distribua o conteudo bruto nos slides seguindo a hierarquia",
                "Cada slide deve ter UM conceito principal claro",
                "Use a regra: se nao suporta o objetivo do slide, remova",
                f"Densidade {density}: {density_advice}",
                "Transforme frases longas em pontos concisos",
                "Mova detalhes para notas do apresentador quando possivel",
            ]
        }

        logger.info(f"Conteudo organizado: {word_count} palavras, densidade {density}")
        return json.dumps(organized, ensure_ascii=False, indent=2)

    except json.JSONDecodeError:
        return json.dumps({
            "status": "error",
            "message": "JSON invalido fornecido"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao organizar conteudo: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def _determine_slide_type(section_name: str, index: int, total: int) -> str:
    """Determina o tipo de slide baseado na secao e posicao."""
    section_lower = section_name.lower()

    if index == 0 and "abertura" in section_lower or "introducao" in section_lower or "gancho" in section_lower:
        return "titulo_impacto"
    elif "dados" in section_lower or "metricas" in section_lower:
        return "dados_graficos"
    elif "prova" in section_lower or "caso" in section_lower or "evidencia" in section_lower:
        return "caso_sucesso"
    elif "cronograma" in section_lower or "timeline" in section_lower:
        return "timeline"
    elif "call to action" in section_lower or "acao" in section_lower or "proposta" in section_lower:
        return "call_to_action"
    elif "resumo" in section_lower or "conclusao" in section_lower:
        return "resumo"
    elif "problema" in section_lower or "desafio" in section_lower:
        return "problema_destaque"
    elif "solucao" in section_lower or "estrategia" in section_lower:
        return "solucao_visual"
    elif index == 0:
        return "secao_titulo"
    else:
        return "conteudo_padrao"


def _suggest_elements(section_name: str, index: int, total: int) -> list:
    """Sugere elementos visuais para cada tipo de slide."""
    section_lower = section_name.lower()

    base = ["titulo", "subtitulo"]

    if any(w in section_lower for w in ["dados", "metricas", "resultado"]):
        return base + ["grafico_barras_ou_linhas", "numero_destaque", "comparativo"]
    elif any(w in section_lower for w in ["prova", "caso", "evidencia"]):
        return base + ["citacao_cliente", "logo", "numeros_impacto"]
    elif any(w in section_lower for w in ["cronograma", "timeline"]):
        return base + ["timeline_horizontal", "marcos", "datas"]
    elif any(w in section_lower for w in ["problema", "desafio"]):
        return base + ["icones_destaque", "estatistica_impacto", "imagem_emocional"]
    elif any(w in section_lower for w in ["solucao", "estrategia"]):
        return base + ["diagrama_fluxo", "icones_features", "antes_depois"]
    elif any(w in section_lower for w in ["call", "acao", "proposta"]):
        return base + ["botao_cta", "contato", "proximo_passo"]
    elif any(w in section_lower for w in ["abertura", "introducao", "gancho"]):
        return base + ["imagem_fullscreen", "frase_impacto"]
    elif any(w in section_lower for w in ["resumo", "conclusao"]):
        return base + ["pontos_chave", "takeaways", "qr_code"]
    else:
        return base + ["bullet_points", "icone_ou_imagem"]
