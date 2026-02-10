"""
FastAPI backend do CRM de Relacionamentos.

Expoe endpoints REST para o frontend consumir dados
de contatos, interacoes, scores, rede e chat com agentes.
"""
import json
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from loguru import logger

# Garantir imports do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.crm_store import (
    add_contact, update_contact, find_contacts, get_contact,
    delete_contact, add_interaction, get_interactions_for_contact,
    get_recent_interactions, get_pending_follow_ups, get_crm_stats,
    load_contacts, load_profile, setup_profile, load_interactions,
)
from tools.relationship_scorer import (
    crm_score_all_relationships, crm_score_contact,
)
from tools.network_analyzer import (
    crm_analyze_network, crm_get_communication_suggestions,
    crm_get_relationship_report,
)
from config.crm_profiles import list_available_profiles, get_profile_defaults

# --- App ---

app = FastAPI(title="CRM de Relacionamentos", version="1.0.0")

WEB_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
templates = Jinja2Templates(directory=WEB_DIR / "templates")


# --- Pydantic request models ---

class ContactCreate(BaseModel):
    nome: str
    categoria: str = "outro"
    email: Optional[str] = None
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    apelido: Optional[str] = None
    notas: Optional[str] = None
    aniversario: Optional[str] = None
    cidade: Optional[str] = None
    como_conheceu: Optional[str] = None
    interesses: list[str] = []
    tags: list[str] = []


class ContactUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    notas: Optional[str] = None
    cidade: Optional[str] = None


class InteractionCreate(BaseModel):
    contato_id: str
    tipo: str
    descricao: str
    sentimento: str = "neutro"
    duracao_minutos: Optional[int] = None
    local: Optional[str] = None
    follow_up_necessario: bool = False
    follow_up_descricao: Optional[str] = None
    tags: list[str] = []


class ProfileSetup(BaseModel):
    nome: str
    tipo: str
    objetivos: list[str] = []


class ChatMessage(BaseModel):
    message: str
    agent: str = "advisor"


# --- Pages ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- API: Dashboard ---

@app.get("/api/dashboard")
async def get_dashboard():
    stats = get_crm_stats()
    profile = load_profile()
    scores_raw = json.loads(crm_score_all_relationships())
    suggestions_raw = json.loads(crm_get_communication_suggestions())
    report_raw = json.loads(crm_get_relationship_report())

    return {
        "stats": stats,
        "profile": profile,
        "scores": scores_raw,
        "suggestions": suggestions_raw.get("sugestoes", [])[:5],
        "report": report_raw.get("relatorio", {}),
    }


# --- API: Contacts ---

@app.get("/api/contacts")
async def list_contacts(
    nome: Optional[str] = None,
    categoria: Optional[str] = None,
    empresa: Optional[str] = None,
):
    results = find_contacts(
        nome=nome or None,
        categoria=categoria or None,
        empresa=empresa or None,
    )
    # Enrich with interaction count
    for c in results:
        ints = get_interactions_for_contact(c["id"])
        c["total_interacoes"] = len(ints)
        if ints:
            sorted_ints = sorted(ints, key=lambda x: x.get("data", ""), reverse=True)
            c["ultima_interacao"] = sorted_ints[0].get("data", "")[:10]
        else:
            c["ultima_interacao"] = None
    return {"contacts": results, "total": len(results)}


@app.get("/api/contacts/{contact_id}")
async def get_contact_detail(contact_id: str):
    contact = get_contact(contact_id)
    if not contact:
        return {"error": "Contato nao encontrado"}
    interactions = get_interactions_for_contact(contact_id)
    interactions.sort(key=lambda x: x.get("data", ""), reverse=True)
    score_raw = json.loads(crm_score_contact(contact_id))
    return {
        "contact": contact,
        "interactions": interactions,
        "score": score_raw.get("score", {}),
    }


@app.post("/api/contacts")
async def create_contact(data: ContactCreate):
    result = add_contact(
        nome=data.nome,
        categoria=data.categoria,
        email=data.email,
        telefone=data.telefone,
        empresa=data.empresa,
        cargo=data.cargo,
        apelido=data.apelido,
        notas=data.notas,
        aniversario=data.aniversario,
        cidade=data.cidade,
        como_conheceu=data.como_conheceu,
        interesses=data.interesses,
        tags=data.tags,
    )
    return {"status": "success", "contact": result}


@app.put("/api/contacts/{contact_id}")
async def update_contact_endpoint(contact_id: str, data: ContactUpdate):
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    result = update_contact(contact_id, **fields)
    if result:
        return {"status": "success", "contact": result}
    return {"status": "error", "message": "Contato nao encontrado"}


@app.delete("/api/contacts/{contact_id}")
async def delete_contact_endpoint(contact_id: str):
    success = delete_contact(contact_id)
    return {"status": "success" if success else "error"}


# --- API: Interactions ---

@app.post("/api/interactions")
async def create_interaction(data: InteractionCreate):
    result = add_interaction(
        contato_id=data.contato_id,
        tipo=data.tipo,
        descricao=data.descricao,
        sentimento=data.sentimento,
        duracao_minutos=data.duracao_minutos,
        local=data.local,
        follow_up_necessario=data.follow_up_necessario,
        follow_up_descricao=data.follow_up_descricao,
        tags=data.tags,
    )
    if result:
        return {"status": "success", "interaction": result}
    return {"status": "error", "message": "Contato nao encontrado"}


@app.get("/api/interactions/recent")
async def recent_interactions(limit: int = 20):
    interactions = get_recent_interactions(limit)
    for i in interactions:
        contact = get_contact(i["contato_id"])
        i["contato_nome"] = contact["nome"] if contact else "Desconhecido"
    return {"interactions": interactions, "total": len(interactions)}


@app.get("/api/interactions/follow-ups")
async def follow_ups():
    fups = get_pending_follow_ups()
    for fu in fups:
        contact = get_contact(fu["contato_id"])
        fu["contato_nome"] = contact["nome"] if contact else "Desconhecido"
    return {"follow_ups": fups, "total": len(fups)}


# --- API: Scores ---

@app.get("/api/scores")
async def get_scores():
    raw = json.loads(crm_score_all_relationships())
    return raw


# --- API: Network ---

@app.get("/api/network")
async def get_network():
    raw = json.loads(crm_analyze_network())
    return raw


@app.get("/api/suggestions")
async def get_suggestions():
    raw = json.loads(crm_get_communication_suggestions())
    return raw


@app.get("/api/report")
async def get_report():
    raw = json.loads(crm_get_relationship_report())
    return raw


# --- API: Profile ---

@app.get("/api/profile")
async def get_profile():
    profile = load_profile()
    if not profile:
        return {"profile": None, "available": list_available_profiles()}
    return {"profile": profile}


@app.post("/api/profile")
async def set_profile(data: ProfileSetup):
    result = setup_profile(
        nome=data.nome,
        tipo=data.tipo,
        objetivos=data.objetivos if data.objetivos else None,
    )
    return {"status": "success", "profile": result}


@app.get("/api/profiles/available")
async def available_profiles():
    return {"profiles": list_available_profiles()}


# --- API: Chat com Agente ---

@app.post("/api/chat")
async def chat_with_agent(data: ChatMessage):
    """Envia mensagem para um agente e retorna a resposta."""
    try:
        from config.settings import OPENAI_API_KEY
        if not OPENAI_API_KEY:
            return {
                "status": "error",
                "message": "OPENAI_API_KEY nao configurada. Configure no .env",
            }

        from agents.priority_advisor import create_priority_advisor
        from agents.relationship_analyst import create_relationship_analyst
        from agents.communication_strategist import create_communication_strategist
        from agents.network_mapper import create_network_mapper

        agents_map = {
            "advisor": create_priority_advisor,
            "analyst": create_relationship_analyst,
            "strategist": create_communication_strategist,
            "mapper": create_network_mapper,
        }

        create_fn = agents_map.get(data.agent, create_priority_advisor)
        agent = create_fn()
        response = agent.run(data.message)

        return {
            "status": "success",
            "response": response.content,
            "agent": agent.name,
        }

    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        return {"status": "error", "message": str(e)}
