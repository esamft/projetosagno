"""
Tools para o Agente Designer Visual

Fornece recomendacoes de layout, paleta de cores, tipografia
e elementos visuais para cada slide da apresentacao.
"""
import json
from loguru import logger


def suggest_slide_layout(
    slide_type: str,
    num_elements: int
) -> str:
    """
    Sugere o layout ideal para um tipo de slide.

    Use esta ferramenta para determinar o melhor layout visual
    para cada slide baseado no seu tipo e quantidade de elementos.

    Args:
        slide_type: Tipo do slide (ex: "titulo_impacto", "dados_graficos", "conteudo_padrao", "call_to_action")
        num_elements: Quantidade de elementos de conteudo no slide

    Returns:
        JSON string com recomendacao de layout detalhada
    """
    try:
        layouts = {
            "titulo_impacto": {
                "layout": "fullscreen_hero",
                "descricao": "Imagem de fundo fullscreen com texto centralizado em overlay",
                "grid": "1 coluna, centralizado vertical",
                "espacamento": "Margens largas (15%+ de cada lado)",
                "alinhamento": "Centro",
                "dicas": [
                    "Use imagem de alta qualidade que evoque emocao",
                    "Texto branco com sombra sutil sobre imagem escurecida",
                    "Maximo 2 linhas de texto",
                    "Fonte grande e bold para o titulo",
                ],
            },
            "dados_graficos": {
                "layout": "split_chart",
                "descricao": "Lado esquerdo com insight textual, lado direito com grafico",
                "grid": "2 colunas (40/60 ou 30/70)",
                "espacamento": "Respiro generoso ao redor do grafico",
                "alinhamento": "Esquerda para texto, centro para grafico",
                "dicas": [
                    "O titulo deve ser o insight, nao a descricao do grafico",
                    "Destaque o numero mais importante em fonte grande",
                    "Simplifique o grafico: menos e mais",
                    "Use cores consistentes com a paleta da apresentacao",
                ],
            },
            "caso_sucesso": {
                "layout": "testimonial",
                "descricao": "Citacao em destaque com logo e resultados numericos",
                "grid": "1 coluna principal com sidebar para metricas",
                "espacamento": "Amplo, aspas grandes decorativas",
                "alinhamento": "Centro para citacao, direita para metricas",
                "dicas": [
                    "Use aspas grandes como elemento decorativo",
                    "Inclua foto ou logo do cliente",
                    "Destaque metricas de resultado em numeros grandes",
                    "Mantenha a citacao curta (maximo 2 linhas)",
                ],
            },
            "timeline": {
                "layout": "horizontal_timeline",
                "descricao": "Linha temporal horizontal com marcos acima e abaixo",
                "grid": "1 coluna, alinhamento horizontal",
                "espacamento": "Uniforme entre marcos",
                "alinhamento": "Centro horizontal",
                "dicas": [
                    "Maximo 5-6 marcos por slide",
                    "Alterne detalhes acima e abaixo da linha",
                    "Use cores para indicar status (feito, em andamento, futuro)",
                    "Destaque o momento atual",
                ],
            },
            "call_to_action": {
                "layout": "centered_cta",
                "descricao": "Mensagem centralizada com acao clara e destaque visual",
                "grid": "1 coluna, centralizado",
                "espacamento": "Muito amplo, slide limpo",
                "alinhamento": "Centro",
                "dicas": [
                    "Uma unica acao clara e especifica",
                    "Use cor de destaque para o CTA",
                    "Inclua informacao de contato se aplicavel",
                    "Menos e mais: maximo 3 elementos no slide",
                ],
            },
            "problema_destaque": {
                "layout": "impact_statement",
                "descricao": "Numero ou frase de impacto grande com contexto minimo",
                "grid": "1 coluna, numero/frase centralizado",
                "espacamento": "Maximizar espaco negativo",
                "alinhamento": "Centro",
                "dicas": [
                    "Um unico numero ou frase de impacto domina o slide",
                    "Use contraste forte (texto escuro em fundo claro ou vice-versa)",
                    "Contexto minimo em fonte pequena abaixo",
                    "Pode usar icone grande como apoio",
                ],
            },
            "solucao_visual": {
                "layout": "feature_grid",
                "descricao": "Grid de features/beneficios com icones",
                "grid": "2x2 ou 3x1 grid de cards",
                "espacamento": "Uniforme entre cards",
                "alinhamento": "Centro dentro de cada card",
                "dicas": [
                    "Cada card: icone + titulo curto + uma linha de descricao",
                    "Maximo 4 cards por slide",
                    "Icones consistentes em estilo",
                    "Use cores para categorizar se necessario",
                ],
            },
            "secao_titulo": {
                "layout": "section_break",
                "descricao": "Slide limpo com nome da secao e breve descricao",
                "grid": "1 coluna, centralizado",
                "espacamento": "Muito amplo",
                "alinhamento": "Centro ou esquerda",
                "dicas": [
                    "Use como pausa visual entre secoes",
                    "Pode usar cor de fundo diferente para distinguir",
                    "Titulo da secao em fonte grande",
                    "Subtitulo opcional em fonte menor",
                ],
            },
            "resumo": {
                "layout": "takeaway_list",
                "descricao": "Lista de pontos-chave com icones de check",
                "grid": "1 coluna, lista vertical",
                "espacamento": "Generoso entre itens",
                "alinhamento": "Esquerda",
                "dicas": [
                    "3-5 takeaways no maximo",
                    "Cada ponto deve ser auto-suficiente",
                    "Use numeracao ou icones para organizar",
                    "Destaque o ponto mais importante",
                ],
            },
        }

        # Fallback para tipo generico
        layout_info = layouts.get(slide_type, {
            "layout": "standard_content",
            "descricao": "Layout padrao com titulo e area de conteudo",
            "grid": f"1 coluna com {min(num_elements, 6)} elementos",
            "espacamento": "Padrao",
            "alinhamento": "Esquerda",
            "dicas": [
                "Mantenha maximo 6 pontos por slide",
                "Use hierarquia visual clara",
                "Deixe espaco negativo suficiente",
            ],
        })

        # Ajusta baseado na quantidade de elementos
        if num_elements > 6:
            layout_info["aviso"] = "Muitos elementos! Considere dividir em 2 slides"
        elif num_elements <= 2:
            layout_info["aviso"] = "Poucos elementos - maximize o espaco visual"

        result = {
            "status": "success",
            "slide_type": slide_type,
            "num_elements": num_elements,
            "layout": layout_info,
        }

        logger.info(f"Layout sugerido: {layout_info['layout']} para tipo '{slide_type}'")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao sugerir layout: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


def recommend_visual_style(
    presentation_type: str,
    audience: str,
    brand_colors: str = ""
) -> str:
    """
    Recomenda estilo visual completo para a apresentacao.

    Use esta ferramenta para definir a identidade visual da apresentacao:
    paleta de cores, tipografia, estilo de imagens e elementos graficos.

    Args:
        presentation_type: Tipo da apresentacao (ex: "Pitch/Venda", "Educacional")
        audience: Descricao do publico-alvo
        brand_colors: Cores da marca em hex separadas por virgula (opcional, ex: "#1a73e8,#34a853")

    Returns:
        JSON string com guia de estilo visual completo
    """
    try:
        audience_lower = audience.lower()

        # Define paletas baseadas no tipo e publico
        if brand_colors:
            colors = [c.strip() for c in brand_colors.split(",")]
            palette_name = "Cores da Marca"
            palette = {
                "primaria": colors[0] if len(colors) > 0 else "#1a73e8",
                "secundaria": colors[1] if len(colors) > 1 else "#5f6368",
                "acento": colors[2] if len(colors) > 2 else "#ea4335",
                "fundo": "#ffffff",
                "texto": "#202124",
                "texto_claro": "#5f6368",
            }
        elif any(w in audience_lower for w in ["executivo", "corporativo", "investidor"]):
            palette_name = "Corporativa Sofisticada"
            palette = {
                "primaria": "#1a237e",
                "secundaria": "#455a64",
                "acento": "#00897b",
                "fundo": "#fafafa",
                "texto": "#212121",
                "texto_claro": "#757575",
            }
        elif any(w in audience_lower for w in ["criativo", "design", "marketing"]):
            palette_name = "Criativa Moderna"
            palette = {
                "primaria": "#6200ea",
                "secundaria": "#00bfa5",
                "acento": "#ff6d00",
                "fundo": "#ffffff",
                "texto": "#1a1a2e",
                "texto_claro": "#6c757d",
            }
        elif any(w in audience_lower for w in ["tecnico", "engenheiro", "dev"]):
            palette_name = "Tech Minimalista"
            palette = {
                "primaria": "#0d47a1",
                "secundaria": "#263238",
                "acento": "#00c853",
                "fundo": "#fafafa",
                "texto": "#212121",
                "texto_claro": "#616161",
            }
        elif any(w in audience_lower for w in ["estudante", "educacao", "academia"]):
            palette_name = "Educacional Acessivel"
            palette = {
                "primaria": "#1565c0",
                "secundaria": "#2e7d32",
                "acento": "#f57c00",
                "fundo": "#ffffff",
                "texto": "#1b1b1b",
                "texto_claro": "#666666",
            }
        else:
            palette_name = "Universal Profissional"
            palette = {
                "primaria": "#1976d2",
                "secundaria": "#455a64",
                "acento": "#ff7043",
                "fundo": "#ffffff",
                "texto": "#212121",
                "texto_claro": "#757575",
            }

        # Define tipografia
        presentation_type_lower = presentation_type.lower()
        if "keynote" in presentation_type_lower or "inspiracional" in presentation_type_lower:
            typography = {
                "titulo": {"fonte": "Montserrat Bold ou Poppins Bold", "tamanho": "36-44pt"},
                "subtitulo": {"fonte": "Montserrat Medium", "tamanho": "20-24pt"},
                "corpo": {"fonte": "Open Sans ou Nunito", "tamanho": "16-18pt"},
                "dados": {"fonte": "Montserrat Bold", "tamanho": "48-72pt"},
            }
        elif "relatorio" in presentation_type_lower or "dados" in presentation_type_lower:
            typography = {
                "titulo": {"fonte": "Roboto Bold ou Inter Bold", "tamanho": "28-36pt"},
                "subtitulo": {"fonte": "Roboto Medium", "tamanho": "18-22pt"},
                "corpo": {"fonte": "Roboto Regular ou Inter", "tamanho": "14-16pt"},
                "dados": {"fonte": "Roboto Mono ou JetBrains Mono", "tamanho": "36-60pt"},
            }
        else:
            typography = {
                "titulo": {"fonte": "Inter Bold ou Lato Bold", "tamanho": "32-40pt"},
                "subtitulo": {"fonte": "Inter Medium", "tamanho": "20-24pt"},
                "corpo": {"fonte": "Inter Regular ou Lato", "tamanho": "16-18pt"},
                "dados": {"fonte": "Inter Bold", "tamanho": "40-64pt"},
            }

        style_guide = {
            "status": "success",
            "guia_visual": {
                "paleta": {
                    "nome": palette_name,
                    "cores": palette,
                    "uso": {
                        "primaria": "Titulos, elementos de destaque, links",
                        "secundaria": "Subtitulos, bordas, separadores",
                        "acento": "CTAs, numeros em destaque, alertas",
                        "fundo": "Background dos slides",
                        "texto": "Corpo do texto principal",
                        "texto_claro": "Textos secundarios, legendas",
                    }
                },
                "tipografia": typography,
                "imagens": {
                    "estilo": "Fotos de alta qualidade ou ilustracoes flat",
                    "formato": "16:9 para fullscreen, quadrado para thumbnails",
                    "filtro": "Consistente em toda a apresentacao",
                    "fontes_sugeridas": ["Unsplash", "Pexels", "Undraw (ilustracoes)"],
                },
                "icones": {
                    "estilo": "Linha fina (outline) ou preenchido, consistente",
                    "tamanho": "48-64px para destaque, 24-32px para inline",
                    "fontes_sugeridas": ["Phosphor Icons", "Feather Icons", "Material Icons"],
                },
                "regras_gerais": [
                    "Maximo 3 cores por slide (primaria + secundaria + acento)",
                    "Consistencia: mesmo estilo de icone em toda a apresentacao",
                    "Espaco negativo: pelo menos 30% do slide deve estar vazio",
                    "Contraste: ratio minimo 4.5:1 para texto sobre fundo",
                    "Alinhamento: use grid invisivel para alinhar todos os elementos",
                ],
            }
        }

        logger.info(f"Estilo visual recomendado: paleta '{palette_name}'")
        return json.dumps(style_guide, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao recomendar estilo: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)
