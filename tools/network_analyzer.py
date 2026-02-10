"""
Ferramenta de analise de rede de relacionamentos.

Mapeia a rede de contatos, identifica clusters, gaps,
pontos fortes e fracos da rede, e gera insights
estrategicos para o usuario.
"""
import json
from collections import Counter
from datetime import datetime, timedelta
from loguru import logger

from storage.crm_store import (
    load_contacts,
    load_interactions,
    load_profile,
    get_interactions_for_contact,
)
from config.crm_profiles import get_profile_defaults


def crm_analyze_network() -> str:
    """
    Faz uma analise completa da rede de relacionamentos.

    Analisa a distribuicao de contatos por categoria, identifica
    gaps na rede, clusters de relacionamento e gera insights
    estrategicos baseados no perfil do usuario.

    Returns:
        JSON com analise completa da rede incluindo:
        - Distribuicao por categoria
        - Saude geral da rede
        - Gaps identificados
        - Clusters
        - Insights e recomendacoes
    """
    try:
        contacts = load_contacts()
        interactions = load_interactions()
        profile = load_profile()

        active = [c for c in contacts if c.get("ativo", True)]

        if not active:
            return json.dumps({
                "status": "success",
                "message": "Rede vazia. Adicione contatos para iniciar a analise.",
                "analise": {},
            }, ensure_ascii=False, indent=2)

        tipo_perfil = profile.get("tipo", "custom")
        defaults = get_profile_defaults(tipo_perfil)
        cats_prioritarias = defaults.get("categorias_prioritarias", [])

        # Distribuicao por categoria
        cat_count = Counter(c.get("categoria", "outro") for c in active)

        # Distribuicao por cidade
        city_count = Counter(c.get("cidade", "Nao informado") or "Nao informado" for c in active)

        # Distribuicao por empresa
        emp_count = Counter(c.get("empresa", "Nao informado") or "Nao informado" for c in active)

        # Tags mais usadas
        all_tags = []
        for c in active:
            all_tags.extend(c.get("tags", []))
        tag_count = Counter(all_tags)

        # Gaps: categorias prioritarias sem contatos suficientes
        gaps = []
        for cat in cats_prioritarias:
            count = cat_count.get(cat, 0)
            if count == 0:
                gaps.append({
                    "tipo": "gap_critico",
                    "categoria": cat,
                    "mensagem": f"Voce nao tem nenhum contato na categoria '{cat}' que e prioritaria para seu perfil",
                    "acao": f"Adicione contatos do tipo '{cat}' para fortalecer sua rede",
                })
            elif count < 3:
                gaps.append({
                    "tipo": "gap_moderado",
                    "categoria": cat,
                    "total": count,
                    "mensagem": f"Poucos contatos ({count}) na categoria prioritaria '{cat}'",
                    "acao": f"Expanda sua rede de '{cat}' para pelo menos 5 contatos",
                })

        # Clusters (agrupamentos por empresa/cidade)
        clusters = []
        for emp, count in emp_count.most_common(5):
            if emp != "Nao informado" and count >= 2:
                cluster_contacts = [c["nome"] for c in active if (c.get("empresa") or "") == emp]
                clusters.append({
                    "tipo": "empresa",
                    "nome": emp,
                    "total_contatos": count,
                    "contatos": cluster_contacts[:5],
                })

        for city, count in city_count.most_common(5):
            if city != "Nao informado" and count >= 2:
                city_contacts = [c["nome"] for c in active if (c.get("cidade") or "") == city]
                clusters.append({
                    "tipo": "cidade",
                    "nome": city,
                    "total_contatos": count,
                    "contatos": city_contacts[:5],
                })

        # Interacoes recentes vs antigas
        now = datetime.now()
        um_mes = now - timedelta(days=30)
        tres_meses = now - timedelta(days=90)

        contatos_ativos_recente = set()
        contatos_ativos_3m = set()
        for i in interactions:
            try:
                d = datetime.fromisoformat(i["data"])
                if d > um_mes:
                    contatos_ativos_recente.add(i["contato_id"])
                if d > tres_meses:
                    contatos_ativos_3m.add(i["contato_id"])
            except (ValueError, KeyError):
                pass

        contatos_inativos = [
            c for c in active if c["id"] not in contatos_ativos_3m
        ]

        # Insights
        insights = []

        # Diversidade da rede
        n_categorias = len(cat_count)
        if n_categorias >= 5:
            insights.append({
                "tipo": "positivo",
                "titulo": "Rede diversificada",
                "descricao": f"Sua rede tem contatos em {n_categorias} categorias diferentes. Boa diversidade!",
            })
        elif n_categorias <= 2:
            insights.append({
                "tipo": "atencao",
                "titulo": "Rede pouco diversificada",
                "descricao": f"Sua rede esta concentrada em apenas {n_categorias} categoria(s). Diversifique!",
                "acao": "Adicione contatos em categorias diferentes para aumentar resiliencia",
            })

        # Atividade
        taxa_atividade = len(contatos_ativos_recente) / len(active) * 100 if active else 0
        if taxa_atividade >= 70:
            insights.append({
                "tipo": "positivo",
                "titulo": "Alta atividade",
                "descricao": f"{taxa_atividade:.0f}% dos seus contatos tiveram interacao no ultimo mes",
            })
        elif taxa_atividade < 30:
            insights.append({
                "tipo": "alerta",
                "titulo": "Baixa atividade na rede",
                "descricao": f"Apenas {taxa_atividade:.0f}% dos contatos tiveram interacao no ultimo mes",
                "acao": "Reserve tempo para entrar em contato com pessoas importantes",
            })

        # Contatos inativos
        if contatos_inativos:
            nomes_inativos = [c["nome"] for c in contatos_inativos[:5]]
            insights.append({
                "tipo": "atencao",
                "titulo": f"{len(contatos_inativos)} contatos inativos (3+ meses)",
                "descricao": f"Contatos sem interacao: {', '.join(nomes_inativos)}{'...' if len(contatos_inativos) > 5 else ''}",
                "acao": "Reative esses relacionamentos ou reavalie se ainda sao relevantes",
            })

        # Volume de interacoes
        tipos_interacao = Counter(i.get("tipo", "") for i in interactions)

        return json.dumps({
            "status": "success",
            "resumo": {
                "total_contatos": len(active),
                "total_interacoes": len(interactions),
                "categorias_ativas": n_categorias,
                "contatos_ativos_ultimo_mes": len(contatos_ativos_recente),
                "contatos_inativos_3_meses": len(contatos_inativos),
                "taxa_atividade_percentual": round(taxa_atividade, 1),
            },
            "distribuicao_categorias": dict(cat_count.most_common()),
            "distribuicao_cidades": dict(city_count.most_common(10)),
            "tags_mais_usadas": dict(tag_count.most_common(10)),
            "tipos_interacao": dict(tipos_interacao.most_common()),
            "gaps": gaps,
            "clusters": clusters,
            "insights": insights,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao analisar rede: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_communication_suggestions() -> str:
    """
    Gera sugestoes inteligentes de comunicacao baseadas no estado
    atual dos relacionamentos e perfil do usuario.

    Analisa todos os contatos e retorna uma lista priorizada de
    quem voce deveria contatar, por que e como.

    Returns:
        JSON com lista priorizada de sugestoes de comunicacao
    """
    try:
        contacts = load_contacts()
        interactions = load_interactions()
        profile = load_profile()

        active = [c for c in contacts if c.get("ativo", True)]
        tipo_perfil = profile.get("tipo", "custom")
        defaults = get_profile_defaults(tipo_perfil)
        freq_config = defaults.get("frequencia_contato_dias", {})
        cats_prioritarias = defaults.get("categorias_prioritarias", [])

        now = datetime.now()
        suggestions = []

        for contact in active:
            categoria = contact.get("categoria", "outro")
            freq_ideal = freq_config.get(categoria, 30)

            contact_interactions = [
                i for i in interactions if i["contato_id"] == contact["id"]
            ]

            # Calcular dias sem contato
            if contact_interactions:
                sorted_ints = sorted(
                    contact_interactions, key=lambda x: x.get("data", ""), reverse=True
                )
                try:
                    last_date = datetime.fromisoformat(sorted_ints[0]["data"])
                    dias = (now - last_date).days
                except (ValueError, KeyError):
                    dias = 999
                ultimo_tipo = sorted_ints[0].get("tipo", "outro")
                ultimo_sentimento = sorted_ints[0].get("sentimento", "neutro")
            else:
                dias = 999
                ultimo_tipo = None
                ultimo_sentimento = None

            # Determinar se precisa de contato
            if dias < freq_ideal:
                continue  # Esta dentro do prazo, nao precisa de sugestao

            # Calcular urgencia
            if dias >= freq_ideal * 3:
                urgencia = "critica"
            elif dias >= freq_ideal * 2:
                urgencia = "alta"
            elif dias >= freq_ideal:
                urgencia = "media"
            else:
                urgencia = "baixa"

            # Ajustar urgencia se categoria e prioritaria
            if categoria in cats_prioritarias[:2] and urgencia == "media":
                urgencia = "alta"

            # Sugerir tipo de comunicacao
            if dias > 90:
                tipo_sugerido = "ligacao"
                motivo = f"Faz {dias} dias sem contato. Uma ligacao mostra interesse genuino"
            elif dias > 60:
                tipo_sugerido = "mensagem"
                motivo = f"Faz {dias} dias sem contato. Envie uma mensagem para retomar"
            elif dias > 30:
                tipo_sugerido = "mensagem"
                motivo = f"Faz {dias} dias sem contato. Hora de manter o vinculo"
            else:
                tipo_sugerido = "mensagem"
                motivo = f"Contato atrasado ({dias} dias). Frequencia ideal: {freq_ideal} dias"

            # Contexto para a mensagem
            contexto_parts = []
            if contact.get("aniversario"):
                try:
                    aniv = datetime.strptime(contact["aniversario"], "%Y-%m-%d")
                    dias_aniv = (aniv.replace(year=now.year) - now).days
                    if dias_aniv < 0:
                        dias_aniv = (aniv.replace(year=now.year + 1) - now).days
                    if dias_aniv <= 14:
                        contexto_parts.append(f"Aniversario em {dias_aniv} dias!")
                except ValueError:
                    pass

            if contact.get("interesses"):
                contexto_parts.append(f"Interesses: {', '.join(contact['interesses'][:3])}")

            if ultimo_sentimento == "negativo":
                contexto_parts.append("Ultima interacao foi negativa - aborde com cuidado")

            # Follow-ups pendentes
            pending_fups = [
                i for i in contact_interactions
                if i.get("follow_up_necessario") and i.get("follow_up_descricao")
            ]
            if pending_fups:
                contexto_parts.append(f"Follow-up pendente: {pending_fups[-1]['follow_up_descricao']}")

            suggestions.append({
                "contato_id": contact["id"],
                "contato_nome": contact["nome"],
                "categoria": categoria,
                "empresa": contact.get("empresa"),
                "tipo_comunicacao": tipo_sugerido,
                "motivo": motivo,
                "urgencia": urgencia,
                "dias_sem_contato": dias,
                "frequencia_ideal_dias": freq_ideal,
                "contexto": " | ".join(contexto_parts) if contexto_parts else None,
            })

        # Ordenar por urgencia
        urgencia_order = {"critica": 0, "alta": 1, "media": 2, "baixa": 3}
        suggestions.sort(key=lambda x: (urgencia_order.get(x["urgencia"], 4), -x["dias_sem_contato"]))

        return json.dumps({
            "status": "success",
            "total_sugestoes": len(suggestions),
            "sugestoes": suggestions,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao gerar sugestoes: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_relationship_report() -> str:
    """
    Gera um relatorio executivo completo sobre o estado dos relacionamentos.

    Combina analise de rede, scores e sugestoes em um relatorio
    unico e acionavel.

    Returns:
        JSON com relatorio completo incluindo metricas, alertas e plano de acao
    """
    try:
        contacts = load_contacts()
        interactions = load_interactions()
        profile = load_profile()

        active = [c for c in contacts if c.get("ativo", True)]

        if not active:
            return json.dumps({
                "status": "success",
                "relatorio": {
                    "mensagem": "CRM vazio. Comece adicionando seus contatos mais importantes!",
                },
            }, ensure_ascii=False, indent=2)

        tipo_perfil = profile.get("tipo", "custom")
        defaults = get_profile_defaults(tipo_perfil)
        freq_config = defaults.get("frequencia_contato_dias", {})

        now = datetime.now()

        # Metricas gerais
        total_ints_30d = 0
        contatos_em_dia = 0
        contatos_atrasados = 0
        contatos_criticos = 0

        for contact in active:
            categoria = contact.get("categoria", "outro")
            freq_ideal = freq_config.get(categoria, 30)

            contact_ints = [i for i in interactions if i["contato_id"] == contact["id"]]
            sorted_ints = sorted(contact_ints, key=lambda x: x.get("data", ""), reverse=True)

            if sorted_ints:
                try:
                    last = datetime.fromisoformat(sorted_ints[0]["data"])
                    dias = (now - last).days
                except (ValueError, KeyError):
                    dias = 999
            else:
                dias = 999

            # Contar interacoes no ultimo mes
            um_mes = now - timedelta(days=30)
            for i in contact_ints:
                try:
                    if datetime.fromisoformat(i["data"]) > um_mes:
                        total_ints_30d += 1
                except (ValueError, KeyError):
                    pass

            if dias <= freq_ideal:
                contatos_em_dia += 1
            elif dias <= freq_ideal * 2:
                contatos_atrasados += 1
            else:
                contatos_criticos += 1

        # Plano de acao semanal
        plano_semanal = []
        for contact in active:
            categoria = contact.get("categoria", "outro")
            freq_ideal = freq_config.get(categoria, 30)

            contact_ints = [i for i in interactions if i["contato_id"] == contact["id"]]
            sorted_ints = sorted(contact_ints, key=lambda x: x.get("data", ""), reverse=True)

            if sorted_ints:
                try:
                    last = datetime.fromisoformat(sorted_ints[0]["data"])
                    dias = (now - last).days
                except (ValueError, KeyError):
                    dias = 999
            else:
                dias = 999

            if dias >= freq_ideal:
                prioridade_num = dias / max(freq_ideal, 1)
                plano_semanal.append({
                    "contato": contact["nome"],
                    "categoria": categoria,
                    "dias_sem_contato": dias,
                    "frequencia_ideal": freq_ideal,
                    "atraso_fator": round(prioridade_num, 1),
                    "acao": "Ligar" if dias > freq_ideal * 3 else "Enviar mensagem",
                })

        plano_semanal.sort(key=lambda x: x["atraso_fator"], reverse=True)

        return json.dumps({
            "status": "success",
            "relatorio": {
                "data": now.strftime("%Y-%m-%d"),
                "perfil": tipo_perfil,
                "metricas": {
                    "total_contatos": len(active),
                    "total_interacoes": len(interactions),
                    "interacoes_ultimos_30_dias": total_ints_30d,
                    "contatos_em_dia": contatos_em_dia,
                    "contatos_atrasados": contatos_atrasados,
                    "contatos_criticos": contatos_criticos,
                    "saude_geral_percentual": round(
                        contatos_em_dia / len(active) * 100, 1
                    ) if active else 0,
                },
                "plano_semanal": plano_semanal[:10],
                "resumo": (
                    f"Dos seus {len(active)} contatos, {contatos_em_dia} estao em dia, "
                    f"{contatos_atrasados} precisam de atencao e {contatos_criticos} estao "
                    f"em situacao critica. Voce teve {total_ints_30d} interacoes nos ultimos 30 dias."
                ),
            },
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao gerar relatorio: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
