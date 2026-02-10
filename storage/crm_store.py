"""
Camada de persistencia do CRM usando arquivos JSON.

Gerencia o armazenamento de contatos, interacoes e perfil do usuario
em arquivos JSON locais no diretorio data/.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

from models.crm import (
    Contact, Interaction, UserProfile, ContactCategory,
    ProfileType, InteractionType
)

# Diretorio de dados
DATA_DIR = Path(__file__).parent.parent / "data"
CONTACTS_FILE = DATA_DIR / "contacts.json"
INTERACTIONS_FILE = DATA_DIR / "interactions.json"
PROFILE_FILE = DATA_DIR / "profile.json"


def _ensure_data_dir():
    """Garante que o diretorio de dados existe"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filepath: Path) -> list | dict:
    """Carrega dados de um arquivo JSON"""
    if not filepath.exists():
        return [] if "profile" not in filepath.name else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logger.warning(f"Arquivo corrompido ou inexistente: {filepath}")
        return [] if "profile" not in filepath.name else {}


def _save_json(filepath: Path, data):
    """Salva dados em um arquivo JSON"""
    _ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_id() -> str:
    """Gera um ID unico curto"""
    return uuid.uuid4().hex[:12]


# --- Contatos ---

def load_contacts() -> list[dict]:
    """Carrega todos os contatos"""
    return _load_json(CONTACTS_FILE)


def save_contacts(contacts: list[dict]):
    """Salva todos os contatos"""
    _save_json(CONTACTS_FILE, contacts)


def add_contact(
    nome: str,
    categoria: str = "outro",
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    empresa: Optional[str] = None,
    cargo: Optional[str] = None,
    apelido: Optional[str] = None,
    notas: Optional[str] = None,
    aniversario: Optional[str] = None,
    cidade: Optional[str] = None,
    como_conheceu: Optional[str] = None,
    interesses: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Adiciona um novo contato ao CRM"""
    contacts = load_contacts()

    contact = Contact(
        id=generate_id(),
        nome=nome,
        apelido=apelido,
        email=email,
        telefone=telefone,
        empresa=empresa,
        cargo=cargo,
        categoria=ContactCategory(categoria),
        tags=tags or [],
        notas=notas,
        aniversario=aniversario,
        cidade=cidade,
        como_conheceu=como_conheceu,
        interesses=interesses or [],
    )

    contact_dict = contact.model_dump()
    contacts.append(contact_dict)
    save_contacts(contacts)

    logger.info(f"Contato adicionado: {nome} (ID: {contact.id})")
    return contact_dict


def update_contact(contact_id: str, **fields) -> Optional[dict]:
    """Atualiza campos de um contato existente"""
    contacts = load_contacts()

    for i, c in enumerate(contacts):
        if c["id"] == contact_id:
            for key, value in fields.items():
                if key in c and value is not None:
                    c[key] = value
            c["atualizado_em"] = datetime.now().isoformat()
            contacts[i] = c
            save_contacts(contacts)
            logger.info(f"Contato atualizado: {contact_id}")
            return c

    logger.warning(f"Contato nao encontrado: {contact_id}")
    return None


def find_contacts(
    nome: Optional[str] = None,
    categoria: Optional[str] = None,
    tag: Optional[str] = None,
    empresa: Optional[str] = None,
    cidade: Optional[str] = None,
) -> list[dict]:
    """Busca contatos por filtros"""
    contacts = load_contacts()
    results = []

    for c in contacts:
        if not c.get("ativo", True):
            continue
        if nome and nome.lower() not in c["nome"].lower():
            continue
        if categoria and c.get("categoria") != categoria:
            continue
        if tag and tag not in c.get("tags", []):
            continue
        if empresa and empresa.lower() not in (c.get("empresa") or "").lower():
            continue
        if cidade and cidade.lower() not in (c.get("cidade") or "").lower():
            continue
        results.append(c)

    return results


def get_contact(contact_id: str) -> Optional[dict]:
    """Busca um contato por ID"""
    contacts = load_contacts()
    for c in contacts:
        if c["id"] == contact_id:
            return c
    return None


def delete_contact(contact_id: str) -> bool:
    """Desativa um contato (soft delete)"""
    result = update_contact(contact_id, ativo=False)
    return result is not None


# --- Interacoes ---

def load_interactions() -> list[dict]:
    """Carrega todas as interacoes"""
    return _load_json(INTERACTIONS_FILE)


def save_interactions(interactions: list[dict]):
    """Salva todas as interacoes"""
    _save_json(INTERACTIONS_FILE, interactions)


def add_interaction(
    contato_id: str,
    tipo: str,
    descricao: str,
    sentimento: Optional[str] = None,
    duracao_minutos: Optional[int] = None,
    local: Optional[str] = None,
    follow_up_necessario: bool = False,
    follow_up_descricao: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Optional[dict]:
    """Registra uma nova interacao com um contato"""
    # Verifica se contato existe
    contact = get_contact(contato_id)
    if not contact:
        logger.warning(f"Contato nao encontrado: {contato_id}")
        return None

    interactions = load_interactions()

    interaction = Interaction(
        id=generate_id(),
        contato_id=contato_id,
        tipo=InteractionType(tipo),
        descricao=descricao,
        sentimento=sentimento,
        duracao_minutos=duracao_minutos,
        local=local,
        follow_up_necessario=follow_up_necessario,
        follow_up_descricao=follow_up_descricao,
        tags=tags or [],
    )

    interaction_dict = interaction.model_dump()
    interactions.append(interaction_dict)
    save_interactions(interactions)

    logger.info(f"Interacao registrada para contato {contato_id}: {tipo}")
    return interaction_dict


def get_interactions_for_contact(contato_id: str) -> list[dict]:
    """Retorna todas as interacoes de um contato especifico"""
    interactions = load_interactions()
    return [i for i in interactions if i["contato_id"] == contato_id]


def get_recent_interactions(limit: int = 20) -> list[dict]:
    """Retorna as interacoes mais recentes"""
    interactions = load_interactions()
    sorted_interactions = sorted(interactions, key=lambda x: x.get("data", ""), reverse=True)
    return sorted_interactions[:limit]


def get_pending_follow_ups() -> list[dict]:
    """Retorna interacoes que precisam de follow-up"""
    interactions = load_interactions()
    return [i for i in interactions if i.get("follow_up_necessario", False)]


# --- Perfil do Usuario ---

def load_profile() -> dict:
    """Carrega o perfil do usuario"""
    return _load_json(PROFILE_FILE)


def save_profile(profile: dict):
    """Salva o perfil do usuario"""
    _save_json(PROFILE_FILE, profile)


def setup_profile(
    nome: str,
    tipo: str,
    objetivos: Optional[list[str]] = None,
) -> dict:
    """Configura o perfil do usuario com defaults baseados no tipo"""
    from config.crm_profiles import get_profile_defaults

    defaults = get_profile_defaults(tipo)

    profile = UserProfile(
        nome=nome,
        tipo=ProfileType(tipo),
        objetivos=objetivos or defaults.get("objetivos", []),
        categorias_prioritarias=[
            ContactCategory(c) for c in defaults.get("categorias_prioritarias", [])
        ],
        frequencia_contato_dias=defaults.get("frequencia_contato_dias", {}),
    )

    profile_dict = profile.model_dump()
    save_profile(profile_dict)
    logger.info(f"Perfil configurado: {nome} ({tipo})")
    return profile_dict


# --- Estatisticas ---

def get_crm_stats() -> dict:
    """Retorna estatisticas gerais do CRM"""
    contacts = load_contacts()
    interactions = load_interactions()
    profile = load_profile()

    active_contacts = [c for c in contacts if c.get("ativo", True)]

    # Contagem por categoria
    categories = {}
    for c in active_contacts:
        cat = c.get("categoria", "outro")
        categories[cat] = categories.get(cat, 0) + 1

    # Contagem de interacoes por tipo
    interaction_types = {}
    for i in interactions:
        t = i.get("tipo", "outro")
        interaction_types[t] = interaction_types.get(t, 0) + 1

    return {
        "total_contatos": len(active_contacts),
        "total_interacoes": len(interactions),
        "contatos_por_categoria": categories,
        "interacoes_por_tipo": interaction_types,
        "follow_ups_pendentes": len(get_pending_follow_ups()),
        "perfil_configurado": bool(profile),
    }
