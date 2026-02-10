"""
Modelos de dados do CRM de Relacionamentos

Define todas as entidades centrais: Contato, Interacao, Relacionamento,
Perfil do usuario e configuracoes por tipo de perfil.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# --- Enums ---

class ProfileType(str, Enum):
    """Tipos de perfil do usuario do CRM"""
    EMPRESARIO = "empresario"
    DIRETOR = "diretor"
    SERVIDOR_PUBLICO = "servidor_publico"
    SAUDE = "saude"
    CUSTOM = "custom"


class ContactCategory(str, Enum):
    """Categorias de contato"""
    FAMILIA = "familia"
    AMIGO_PROXIMO = "amigo_proximo"
    COLEGA_TRABALHO = "colega_trabalho"
    CLIENTE = "cliente"
    FORNECEDOR = "fornecedor"
    PARCEIRO = "parceiro"
    MENTOR = "mentor"
    MENTORADO = "mentorado"
    NETWORKING = "networking"
    GOVERNO = "governo"
    INVESTIDOR = "investidor"
    PACIENTE = "paciente"
    REFERENCIA_MEDICA = "referencia_medica"
    OUTRO = "outro"


class InteractionType(str, Enum):
    """Tipos de interacao registrada"""
    MENSAGEM = "mensagem"
    LIGACAO = "ligacao"
    REUNIAO = "reuniao"
    EMAIL = "email"
    ENCONTRO_PRESENCIAL = "encontro_presencial"
    REDE_SOCIAL = "rede_social"
    EVENTO = "evento"
    FAVOR_FEITO = "favor_feito"
    FAVOR_RECEBIDO = "favor_recebido"
    INDICACAO = "indicacao"
    PRESENTE = "presente"
    OUTRO = "outro"


class RelationshipStrength(str, Enum):
    """Nivel de forca do relacionamento"""
    FORTE = "forte"
    MODERADO = "moderado"
    FRACO = "fraco"
    ESFRIANDO = "esfriando"
    PERDIDO = "perdido"


class Priority(str, Enum):
    """Prioridade de contato"""
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


# --- Modelos ---

class Contact(BaseModel):
    """Representa um contato no CRM"""
    id: str = Field(description="ID unico do contato")
    nome: str = Field(description="Nome completo")
    apelido: Optional[str] = Field(default=None, description="Apelido ou como prefere ser chamado")
    email: Optional[str] = Field(default=None)
    telefone: Optional[str] = Field(default=None)
    empresa: Optional[str] = Field(default=None, description="Empresa ou organizacao")
    cargo: Optional[str] = Field(default=None)
    categoria: ContactCategory = Field(default=ContactCategory.OUTRO)
    tags: list[str] = Field(default_factory=list, description="Tags livres para classificacao")
    notas: Optional[str] = Field(default=None, description="Notas pessoais sobre o contato")
    aniversario: Optional[str] = Field(default=None, description="Data de aniversario (YYYY-MM-DD)")
    cidade: Optional[str] = Field(default=None)
    como_conheceu: Optional[str] = Field(default=None, description="Como voce conheceu essa pessoa")
    interesses: list[str] = Field(default_factory=list, description="Interesses conhecidos")
    criado_em: str = Field(default_factory=lambda: datetime.now().isoformat())
    atualizado_em: str = Field(default_factory=lambda: datetime.now().isoformat())
    ativo: bool = Field(default=True)


class Interaction(BaseModel):
    """Representa uma interacao com um contato"""
    id: str = Field(description="ID unico da interacao")
    contato_id: str = Field(description="ID do contato")
    tipo: InteractionType = Field(description="Tipo de interacao")
    descricao: str = Field(description="Descricao breve do que aconteceu")
    sentimento: Optional[str] = Field(
        default=None,
        description="Sentimento da interacao: positivo, neutro, negativo"
    )
    data: str = Field(default_factory=lambda: datetime.now().isoformat())
    duracao_minutos: Optional[int] = Field(default=None)
    local: Optional[str] = Field(default=None)
    follow_up_necessario: bool = Field(default=False)
    follow_up_descricao: Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)


class RelationshipScore(BaseModel):
    """Score calculado de saude do relacionamento"""
    contato_id: str
    contato_nome: str
    score: float = Field(ge=0, le=100, description="Score de 0 a 100")
    forca: RelationshipStrength
    dias_sem_contato: int
    total_interacoes: int
    interacoes_ultimo_mes: int
    sentimento_medio: str = Field(description="positivo, neutro ou negativo")
    tendencia: str = Field(description="melhorando, estavel, piorando")
    alerta: Optional[str] = Field(default=None, description="Alerta se precisa de atencao")
    sugestao: Optional[str] = Field(default=None, description="Sugestao de proxima acao")
    prioridade: Priority = Field(default=Priority.MEDIA)
    calculado_em: str = Field(default_factory=lambda: datetime.now().isoformat())


class UserProfile(BaseModel):
    """Perfil do usuario do CRM"""
    nome: str = Field(description="Nome do usuario")
    tipo: ProfileType = Field(description="Tipo de perfil")
    objetivos: list[str] = Field(
        default_factory=list,
        description="Objetivos de relacionamento do usuario"
    )
    categorias_prioritarias: list[ContactCategory] = Field(
        default_factory=list,
        description="Categorias de contato mais importantes para este perfil"
    )
    frequencia_contato_dias: dict[str, int] = Field(
        default_factory=dict,
        description="Frequencia ideal de contato por categoria (em dias)"
    )
    criado_em: str = Field(default_factory=lambda: datetime.now().isoformat())


class NetworkInsight(BaseModel):
    """Insight sobre a rede de relacionamentos"""
    tipo: str = Field(description="Tipo do insight: gap, oportunidade, risco, padrao")
    titulo: str
    descricao: str
    contatos_envolvidos: list[str] = Field(default_factory=list)
    acao_sugerida: Optional[str] = Field(default=None)
    prioridade: Priority = Field(default=Priority.MEDIA)


class CommunicationSuggestion(BaseModel):
    """Sugestao de comunicacao gerada pelo agente"""
    contato_id: str
    contato_nome: str
    tipo_comunicacao: InteractionType
    mensagem_sugerida: Optional[str] = Field(default=None)
    motivo: str
    urgencia: Priority
    melhor_horario: Optional[str] = Field(default=None)
    contexto: Optional[str] = Field(default=None, description="Contexto relevante para a comunicacao")
