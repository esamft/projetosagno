"""
Ferramenta de gerenciamento de perfil do usuario do CRM.

Permite configurar, visualizar e atualizar o perfil do usuario,
incluindo tipo de perfil, objetivos e preferencias.
"""
import json
from loguru import logger

from storage.crm_store import load_profile, save_profile, setup_profile
from config.crm_profiles import list_available_profiles, get_profile_defaults


def crm_setup_profile(
    nome: str,
    tipo: str,
    objetivos: str = "",
) -> str:
    """
    Configura o perfil do usuario no CRM.

    Define o tipo de perfil (empresario, diretor, servidor_publico, saude, custom)
    que personaliza todo o comportamento do CRM: prioridades, frequencias
    de contato e sugestoes dos agentes.

    Tipos disponiveis:
    - empresario: Foco em clientes, parceiros e networking comercial
    - diretor: Foco em equipe, stakeholders e aliancas internas
    - servidor_publico: Foco em relacoes institucionais e parcerias
    - saude: Foco em pacientes, referencias medicas e comunidade cientifica
    - custom: Perfil personalizado

    Args:
        nome: Seu nome (obrigatorio)
        tipo: Tipo de perfil (obrigatorio)
        objetivos: Objetivos separados por ponto-e-virgula (opcional, usa defaults se vazio)

    Returns:
        JSON com o perfil configurado
    """
    try:
        obj_list = [o.strip() for o in objetivos.split(";") if o.strip()] if objetivos else None

        result = setup_profile(
            nome=nome,
            tipo=tipo,
            objetivos=obj_list,
        )

        return json.dumps({
            "status": "success",
            "message": f"Perfil configurado com sucesso para {nome} ({tipo})",
            "perfil": result,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao configurar perfil: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_get_profile() -> str:
    """
    Retorna o perfil atual do usuario do CRM.

    Mostra todas as configuracoes do perfil incluindo tipo,
    objetivos, categorias prioritarias e frequencias de contato.

    Returns:
        JSON com o perfil do usuario
    """
    try:
        profile = load_profile()

        if not profile:
            return json.dumps({
                "status": "success",
                "message": "Perfil ainda nao configurado. Use crm_setup_profile para configurar.",
                "perfis_disponiveis": list_available_profiles(),
            }, ensure_ascii=False, indent=2)

        return json.dumps({
            "status": "success",
            "perfil": profile,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao obter perfil: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def crm_list_profiles() -> str:
    """
    Lista todos os perfis disponiveis para configuracao.

    Mostra os tipos de perfil que podem ser escolhidos,
    com descricao e foco de cada um.

    Returns:
        JSON com lista de perfis disponiveis
    """
    try:
        profiles = list_available_profiles()

        return json.dumps({
            "status": "success",
            "perfis": profiles,
            "instrucao": "Use crm_setup_profile(nome, tipo) para configurar seu perfil",
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao listar perfis: {e}")
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
