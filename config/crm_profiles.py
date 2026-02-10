"""
Configuracoes de perfil especificas para cada tipo de usuario do CRM.

Cada perfil define:
- Objetivos de relacionamento
- Categorias prioritarias de contato
- Frequencia ideal de contato por categoria (em dias)
- Instrucoes especializadas para os agentes
"""


PROFILE_DEFAULTS = {
    "empresario": {
        "objetivos": [
            "Manter relacionamentos estrategicos com clientes-chave",
            "Expandir rede de parceiros e fornecedores",
            "Cultivar relacoes com investidores e mentores",
            "Fortalecer networking em eventos do setor",
            "Gerar novas oportunidades de negocio via indicacoes",
        ],
        "categorias_prioritarias": [
            "cliente",
            "parceiro",
            "investidor",
            "fornecedor",
            "mentor",
            "networking",
        ],
        "frequencia_contato_dias": {
            "cliente": 7,
            "parceiro": 14,
            "investidor": 21,
            "fornecedor": 30,
            "mentor": 14,
            "networking": 30,
            "familia": 3,
            "amigo_proximo": 7,
            "colega_trabalho": 14,
        },
        "instrucoes_agente": (
            "Voce esta assessorando um empresario. Priorize relacionamentos "
            "que geram valor comercial direto: clientes-chave, parceiros estrategicos "
            "e investidores. Sugira acoes de networking que ampliem a rede de negocios. "
            "Lembre-o de manter relacoes pessoais (familia, amigos) que sao a base "
            "do bem-estar e produtividade."
        ),
    },

    "diretor": {
        "objetivos": [
            "Gerenciar relacionamentos com equipe e subordinados diretos",
            "Manter comunicacao eficaz com board e stakeholders",
            "Cultivar aliancas internas entre departamentos",
            "Desenvolver mentorados e talentos-chave",
            "Representar a organizacao em relacoes externas",
        ],
        "categorias_prioritarias": [
            "colega_trabalho",
            "mentorado",
            "parceiro",
            "cliente",
            "networking",
        ],
        "frequencia_contato_dias": {
            "colega_trabalho": 3,
            "mentorado": 7,
            "parceiro": 14,
            "cliente": 14,
            "networking": 21,
            "familia": 3,
            "amigo_proximo": 7,
        },
        "instrucoes_agente": (
            "Voce esta assessorando um diretor/executivo. Priorize a gestao "
            "de relacionamentos com a equipe direta e stakeholders. Sugira acoes "
            "que fortaleam aliancas internas e desenvolvimento de talentos. "
            "Lembre de reunioes one-on-one, feedbacks e momentos de reconhecimento. "
            "Equilibre demandas profissionais com relacoes pessoais."
        ),
    },

    "servidor_publico": {
        "objetivos": [
            "Manter rede de contatos institucionais atualizada",
            "Fortalecer relacoes interinstitucionais",
            "Cultivar relacionamentos com a comunidade",
            "Manter comunicacao transparente com superiores",
            "Desenvolver parcerias publico-privadas estrategicas",
        ],
        "categorias_prioritarias": [
            "governo",
            "colega_trabalho",
            "parceiro",
            "networking",
            "mentor",
        ],
        "frequencia_contato_dias": {
            "governo": 7,
            "colega_trabalho": 5,
            "parceiro": 14,
            "networking": 21,
            "mentor": 14,
            "familia": 3,
            "amigo_proximo": 7,
        },
        "instrucoes_agente": (
            "Voce esta assessorando um servidor publico. Priorize relacionamentos "
            "institucionais e interinstitucionais. Sugira acoes que fortaleam "
            "a rede de contatos governamentais e parcerias estrategicas. "
            "Lembre que transparencia e etica sao fundamentais. "
            "Ajude a equilibrar a vida publica com relacoes pessoais."
        ),
    },

    "saude": {
        "objetivos": [
            "Manter relacionamento proximo com pacientes-chave",
            "Cultivar rede de referencias medicas",
            "Participar ativamente de comunidades cientificas",
            "Fortalecer relacoes com colegas de especialidade",
            "Desenvolver mentoria com profissionais mais jovens",
        ],
        "categorias_prioritarias": [
            "paciente",
            "referencia_medica",
            "colega_trabalho",
            "mentor",
            "mentorado",
            "networking",
        ],
        "frequencia_contato_dias": {
            "paciente": 30,
            "referencia_medica": 14,
            "colega_trabalho": 7,
            "mentor": 14,
            "mentorado": 14,
            "networking": 30,
            "familia": 3,
            "amigo_proximo": 7,
        },
        "instrucoes_agente": (
            "Voce esta assessorando um profissional de saude. Priorize o "
            "acompanhamento de pacientes e a rede de referencias medicas. "
            "Sugira participacao em congressos e comunidades cientificas. "
            "Lembre da importancia do autocuidado e relacoes pessoais "
            "para evitar burnout. Respeite sempre a etica medica."
        ),
    },

    "custom": {
        "objetivos": [
            "Manter relacionamentos pessoais saudaveis",
            "Expandir rede de contatos profissionais",
            "Cultivar amizades significativas",
        ],
        "categorias_prioritarias": [
            "familia",
            "amigo_proximo",
            "colega_trabalho",
            "networking",
        ],
        "frequencia_contato_dias": {
            "familia": 3,
            "amigo_proximo": 7,
            "colega_trabalho": 14,
            "networking": 30,
        },
        "instrucoes_agente": (
            "Voce esta assessorando uma pessoa com perfil personalizado. "
            "Adapte suas sugestoes com base nos objetivos e categorias "
            "prioritarias configuradas pelo usuario."
        ),
    },
}


def get_profile_defaults(tipo: str) -> dict:
    """Retorna os defaults para um tipo de perfil"""
    return PROFILE_DEFAULTS.get(tipo, PROFILE_DEFAULTS["custom"])


def get_agent_instructions(tipo: str) -> str:
    """Retorna as instrucoes especializadas do agente para o perfil"""
    defaults = get_profile_defaults(tipo)
    return defaults.get("instrucoes_agente", PROFILE_DEFAULTS["custom"]["instrucoes_agente"])


def list_available_profiles() -> list[dict]:
    """Lista os perfis disponiveis com descricao"""
    return [
        {
            "tipo": "empresario",
            "descricao": "Empresario, empreendedor ou dono de negocio",
            "foco": "Clientes, parceiros, investidores e networking comercial",
        },
        {
            "tipo": "diretor",
            "descricao": "Diretor, executivo ou gestor de equipes",
            "foco": "Equipe, stakeholders, mentorados e aliancas internas",
        },
        {
            "tipo": "servidor_publico",
            "descricao": "Servidor publico ou profissional do governo",
            "foco": "Relacoes institucionais, parcerias e comunidade",
        },
        {
            "tipo": "saude",
            "descricao": "Medico, enfermeiro ou profissional de saude",
            "foco": "Pacientes, referencias medicas e comunidade cientifica",
        },
        {
            "tipo": "custom",
            "descricao": "Perfil personalizado",
            "foco": "Configuracao livre conforme suas necessidades",
        },
    ]
