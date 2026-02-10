"""
Ferramenta de gerenciamento de contatos do CRM.

Permite adicionar, buscar, atualizar e visualizar contatos
e suas interacoes. Funciona como a interface principal
dos agentes com os dados de contatos.
"""
import json
from typing import Optional
from loguru import logger

from storage.crm_store import (
    add_contact,
    update_contact,
    find_contacts,
    get_contact,
    delete_contact,
    add_interaction,
    get_interactions_for_contact,
    get_recent_interactions,
    get_pending_follow_ups,
    get_crm_stats,
    load_contacts,
)


def crm_add_contact(
    nome: str,
    categoria: str = "outro",
    email: str = "",
    telefone: str = "",
    empresa: str = "",
    cargo: str = "",
    apelido: str = "",
    notas: str = "",
    aniversario: str = "",
    cidade: str = "",
    como_conheceu: str = "",
    interesses: str = "",
    tags: str = "",
) -> str:
    """
    Adiciona um novo contato ao CRM de relacionamentos.

    Use esta ferramenta para cadastrar uma nova pessoa na base de contatos.
    O campo 'nome' e obrigatorio. Todos os outros sao opcionais.

    Categorias validas: familia, amigo_proximo, colega_trabalho, cliente,
    fornecedor, parceiro, mentor, mentorado, networking, governo, investidor,
    paciente, referencia_medica, outro.

    Args:
        nome: Nome completo da pessoa (obrigatorio)
        categoria: Categoria do contato (ex: cliente, parceiro, familia)
        email: Email do contato
        telefone: Telefone do contato
        empresa: Empresa ou organizacao
        cargo: Cargo ou funcao
        apelido: Apelido ou como prefere ser chamado
        notas: Notas pessoais sobre o contato
        aniversario: Data de aniversario no formato YYYY-MM-DD
        cidade: Cidade onde mora
        como_conheceu: Como voce conheceu essa pessoa
        interesses: Interesses da pessoa, separados por virgula
        tags: Tags para classificacao, separadas por virgula

    Returns:
        JSON com os dados do contato criado
    """
    try:
        interesses_list = [i.strip() for i in interesses.split(",") if i.strip()] if interesses else []
        tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        result = add_contact(
            nome=nome,
            categoria=categoria if categoria else "outro",
            email=email or None,
            telefone=telefone or None,
            empresa=empresa or None,
            cargo=cargo or None,
            apelido=apelido or None,
            notas=notas or None,
            aniversario=aniversario or None,
            cidade=cidade or None,
            como_conheceu=como_conheceu or None,
            interesses=interesses_list,
            tags=tags_list,
        )

        return json.dumps({
            "status": "success",
            "message": f"Contato '{nome}' adicionado com sucesso",
            "contato": result,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao adicionar contato: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_search_contacts(
    nome: str = "",
    categoria: str = "",
    tag: str = "",
    empresa: str = "",
    cidade: str = "",
) -> str:
    """
    Busca contatos no CRM por nome, categoria, tag, empresa ou cidade.

    Use esta ferramenta para encontrar contatos existentes na base.
    Todos os filtros sao opcionais e combinaveis.

    Args:
        nome: Filtrar por nome (busca parcial)
        categoria: Filtrar por categoria (ex: cliente, parceiro)
        tag: Filtrar por tag especifica
        empresa: Filtrar por empresa (busca parcial)
        cidade: Filtrar por cidade (busca parcial)

    Returns:
        JSON com lista de contatos encontrados
    """
    try:
        results = find_contacts(
            nome=nome or None,
            categoria=categoria or None,
            tag=tag or None,
            empresa=empresa or None,
            cidade=cidade or None,
        )

        return json.dumps({
            "status": "success",
            "total": len(results),
            "contatos": results,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao buscar contatos: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_contact_details(contact_id: str) -> str:
    """
    Retorna os detalhes completos de um contato, incluindo historico de interacoes.

    Use esta ferramenta para ver o perfil completo de um contato e todas
    as interacoes registradas com ele.

    Args:
        contact_id: ID do contato

    Returns:
        JSON com dados do contato e historico de interacoes
    """
    try:
        contact = get_contact(contact_id)
        if not contact:
            return json.dumps({
                "status": "error",
                "message": f"Contato nao encontrado: {contact_id}"
            }, ensure_ascii=False)

        interactions = get_interactions_for_contact(contact_id)
        interactions_sorted = sorted(
            interactions, key=lambda x: x.get("data", ""), reverse=True
        )

        return json.dumps({
            "status": "success",
            "contato": contact,
            "total_interacoes": len(interactions),
            "interacoes": interactions_sorted,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao obter detalhes: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_update_contact(
    contact_id: str,
    nome: str = "",
    categoria: str = "",
    email: str = "",
    telefone: str = "",
    empresa: str = "",
    cargo: str = "",
    notas: str = "",
    cidade: str = "",
) -> str:
    """
    Atualiza informacoes de um contato existente.

    Use esta ferramenta para modificar dados de um contato ja cadastrado.
    Apenas os campos preenchidos serao atualizados.

    Args:
        contact_id: ID do contato a ser atualizado (obrigatorio)
        nome: Novo nome
        categoria: Nova categoria
        email: Novo email
        telefone: Novo telefone
        empresa: Nova empresa
        cargo: Novo cargo
        notas: Novas notas
        cidade: Nova cidade

    Returns:
        JSON com o contato atualizado
    """
    try:
        fields = {}
        if nome:
            fields["nome"] = nome
        if categoria:
            fields["categoria"] = categoria
        if email:
            fields["email"] = email
        if telefone:
            fields["telefone"] = telefone
        if empresa:
            fields["empresa"] = empresa
        if cargo:
            fields["cargo"] = cargo
        if notas:
            fields["notas"] = notas
        if cidade:
            fields["cidade"] = cidade

        if not fields:
            return json.dumps({
                "status": "error",
                "message": "Nenhum campo para atualizar"
            }, ensure_ascii=False)

        result = update_contact(contact_id, **fields)
        if result:
            return json.dumps({
                "status": "success",
                "message": "Contato atualizado com sucesso",
                "contato": result,
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": f"Contato nao encontrado: {contact_id}"
            }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Erro ao atualizar contato: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_register_interaction(
    contato_id: str,
    tipo: str,
    descricao: str,
    sentimento: str = "neutro",
    duracao_minutos: str = "",
    local: str = "",
    follow_up_necessario: str = "nao",
    follow_up_descricao: str = "",
    tags: str = "",
) -> str:
    """
    Registra uma interacao (comunicacao) com um contato.

    Use esta ferramenta para registrar qualquer tipo de contato que voce
    teve com uma pessoa: mensagem, ligacao, reuniao, encontro, etc.

    Tipos validos: mensagem, ligacao, reuniao, email, encontro_presencial,
    rede_social, evento, favor_feito, favor_recebido, indicacao, presente, outro.

    Sentimentos: positivo, neutro, negativo.

    Args:
        contato_id: ID do contato (obrigatorio)
        tipo: Tipo de interacao (obrigatorio)
        descricao: O que aconteceu nessa interacao (obrigatorio)
        sentimento: positivo, neutro ou negativo
        duracao_minutos: Duracao em minutos (numerico)
        local: Onde aconteceu
        follow_up_necessario: 'sim' ou 'nao' - se precisa de acompanhamento
        follow_up_descricao: Descricao do follow-up necessario
        tags: Tags separadas por virgula

    Returns:
        JSON com os dados da interacao registrada
    """
    try:
        tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        dur = int(duracao_minutos) if duracao_minutos.strip() else None
        follow_up = follow_up_necessario.lower().strip() in ("sim", "s", "yes", "true", "1")

        result = add_interaction(
            contato_id=contato_id,
            tipo=tipo,
            descricao=descricao,
            sentimento=sentimento or "neutro",
            duracao_minutos=dur,
            local=local or None,
            follow_up_necessario=follow_up,
            follow_up_descricao=follow_up_descricao or None,
            tags=tags_list,
        )

        if result:
            return json.dumps({
                "status": "success",
                "message": "Interacao registrada com sucesso",
                "interacao": result,
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": f"Contato nao encontrado: {contato_id}"
            }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Erro ao registrar interacao: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_recent_activity(limit: str = "20") -> str:
    """
    Retorna as interacoes mais recentes de todo o CRM.

    Use esta ferramenta para ver a atividade recente e ter uma visao
    geral do que esta acontecendo nos seus relacionamentos.

    Args:
        limit: Numero maximo de interacoes a retornar (padrao: 20)

    Returns:
        JSON com as interacoes mais recentes
    """
    try:
        lim = int(limit) if limit.strip() else 20
        interactions = get_recent_interactions(lim)

        # Enriquece com nome do contato
        enriched = []
        for i in interactions:
            contact = get_contact(i["contato_id"])
            i["contato_nome"] = contact["nome"] if contact else "Desconhecido"
            enriched.append(i)

        return json.dumps({
            "status": "success",
            "total": len(enriched),
            "interacoes": enriched,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao obter atividade recente: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_follow_ups() -> str:
    """
    Retorna todas as interacoes que precisam de follow-up.

    Use esta ferramenta para ver quais contatos precisam de
    acompanhamento e qual acao tomar.

    Returns:
        JSON com interacoes pendentes de follow-up
    """
    try:
        follow_ups = get_pending_follow_ups()

        enriched = []
        for fu in follow_ups:
            contact = get_contact(fu["contato_id"])
            fu["contato_nome"] = contact["nome"] if contact else "Desconhecido"
            enriched.append(fu)

        return json.dumps({
            "status": "success",
            "total": len(enriched),
            "follow_ups": enriched,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao obter follow-ups: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_stats() -> str:
    """
    Retorna estatisticas gerais do CRM.

    Use esta ferramenta para ter uma visao geral da base de contatos,
    total de interacoes e distribuicao por categorias.

    Returns:
        JSON com estatisticas do CRM
    """
    try:
        stats = get_crm_stats()
        return json.dumps({
            "status": "success",
            "estatisticas": stats,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao obter estatisticas: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_list_all_contacts() -> str:
    """
    Lista todos os contatos ativos no CRM com um resumo de cada um.

    Use esta ferramenta para obter uma visao geral de todos os contatos
    cadastrados no CRM.

    Returns:
        JSON com lista resumida de todos os contatos ativos
    """
    try:
        contacts = load_contacts()
        active = [c for c in contacts if c.get("ativo", True)]

        summaries = []
        for c in active:
            interactions = get_interactions_for_contact(c["id"])
            last_interaction = None
            if interactions:
                sorted_ints = sorted(interactions, key=lambda x: x.get("data", ""), reverse=True)
                last_interaction = sorted_ints[0].get("data", "")[:10]

            summaries.append({
                "id": c["id"],
                "nome": c["nome"],
                "categoria": c.get("categoria", "outro"),
                "empresa": c.get("empresa"),
                "cidade": c.get("cidade"),
                "total_interacoes": len(interactions),
                "ultima_interacao": last_interaction,
                "tags": c.get("tags", []),
            })

        return json.dumps({
            "status": "success",
            "total": len(summaries),
            "contatos": summaries,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao listar contatos: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
