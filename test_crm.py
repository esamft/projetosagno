"""
Testes do CRM de Relacionamentos

Testa modelos, storage, tools e fluxos completos
sem necessidade de API key (nao testa agentes LLM).

Executar: python test_crm.py
"""
import json
import os
import sys
import shutil
from pathlib import Path

# Garantir que o diretorio raiz esta no path
sys.path.insert(0, str(Path(__file__).parent))

# Usar diretorio temporario para testes
TEST_DATA_DIR = Path(__file__).parent / "data_test"


def setup_test_env():
    """Configura ambiente de teste com diretorio temporario"""
    import storage.crm_store as store
    store.DATA_DIR = TEST_DATA_DIR
    store.CONTACTS_FILE = TEST_DATA_DIR / "contacts.json"
    store.INTERACTIONS_FILE = TEST_DATA_DIR / "interactions.json"
    store.PROFILE_FILE = TEST_DATA_DIR / "profile.json"
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_test_env():
    """Remove diretorio de teste"""
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


def test_models():
    """Testa criacao dos modelos Pydantic"""
    print("\n--- Testando Modelos ---")

    from models.crm import (
        Contact, Interaction, RelationshipScore, UserProfile,
        ContactCategory, InteractionType, ProfileType
    )

    # Contact
    contact = Contact(
        id="test123",
        nome="Maria Silva",
        categoria=ContactCategory.CLIENTE,
        email="maria@test.com",
        empresa="Tech Corp",
        tags=["vip", "tech"],
    )
    assert contact.nome == "Maria Silva"
    assert contact.categoria == ContactCategory.CLIENTE
    print("  [OK] Contact model")

    # Interaction
    interaction = Interaction(
        id="int456",
        contato_id="test123",
        tipo=InteractionType.REUNIAO,
        descricao="Reuniao de alinhamento",
        sentimento="positivo",
    )
    assert interaction.tipo == InteractionType.REUNIAO
    print("  [OK] Interaction model")

    # UserProfile
    profile = UserProfile(
        nome="Joao",
        tipo=ProfileType.EMPRESARIO,
        objetivos=["Expandir networking"],
    )
    assert profile.tipo == ProfileType.EMPRESARIO
    print("  [OK] UserProfile model")

    print("  Todos os modelos OK!")


def test_profiles():
    """Testa configuracoes de perfil"""
    print("\n--- Testando Profiles ---")

    from config.crm_profiles import (
        get_profile_defaults, get_agent_instructions, list_available_profiles
    )

    # Defaults por tipo
    for tipo in ["empresario", "diretor", "servidor_publico", "saude", "custom"]:
        defaults = get_profile_defaults(tipo)
        assert "objetivos" in defaults
        assert "categorias_prioritarias" in defaults
        assert "frequencia_contato_dias" in defaults
        print(f"  [OK] Defaults para '{tipo}': {len(defaults['objetivos'])} objetivos")

    # Instrucoes de agente
    for tipo in ["empresario", "diretor", "servidor_publico", "saude", "custom"]:
        instrucoes = get_agent_instructions(tipo)
        assert len(instrucoes) > 50
        print(f"  [OK] Instrucoes para '{tipo}': {len(instrucoes)} chars")

    # Lista de perfis
    profiles = list_available_profiles()
    assert len(profiles) == 5
    print(f"  [OK] {len(profiles)} perfis disponiveis")

    print("  Todos os profiles OK!")


def test_storage():
    """Testa operacoes de storage"""
    print("\n--- Testando Storage ---")

    from storage.crm_store import (
        add_contact, find_contacts, get_contact, update_contact,
        delete_contact, add_interaction, get_interactions_for_contact,
        get_recent_interactions, get_pending_follow_ups, setup_profile,
        load_profile, get_crm_stats
    )

    # Adicionar contatos
    c1 = add_contact("Ana Paula", categoria="cliente", empresa="ABC Ltda", cidade="Sao Paulo")
    assert c1["nome"] == "Ana Paula"
    c1_id = c1["id"]
    print(f"  [OK] Contato adicionado: {c1['nome']} (ID: {c1_id})")

    c2 = add_contact("Carlos Souza", categoria="parceiro", empresa="XYZ Corp", tags=["tech"])
    c2_id = c2["id"]
    print(f"  [OK] Contato adicionado: {c2['nome']} (ID: {c2_id})")

    c3 = add_contact("Dra. Lucia", categoria="referencia_medica", cidade="Sao Paulo")
    c3_id = c3["id"]
    print(f"  [OK] Contato adicionado: {c3['nome']} (ID: {c3_id})")

    # Buscar contatos
    results = find_contacts(nome="Ana")
    assert len(results) == 1
    print(f"  [OK] Busca por nome: {len(results)} resultado(s)")

    results = find_contacts(cidade="Sao Paulo")
    assert len(results) == 2
    print(f"  [OK] Busca por cidade: {len(results)} resultado(s)")

    results = find_contacts(categoria="cliente")
    assert len(results) == 1
    print(f"  [OK] Busca por categoria: {len(results)} resultado(s)")

    # Atualizar contato
    updated = update_contact(c1_id, cargo="Diretora")
    assert updated["cargo"] == "Diretora"
    print(f"  [OK] Contato atualizado: cargo={updated['cargo']}")

    # Get por ID
    contact = get_contact(c1_id)
    assert contact is not None
    print(f"  [OK] Get por ID: {contact['nome']}")

    # Adicionar interacoes
    i1 = add_interaction(c1_id, "reuniao", "Reuniao de kick-off do projeto", sentimento="positivo")
    assert i1 is not None
    print(f"  [OK] Interacao adicionada: {i1['tipo']}")

    i2 = add_interaction(c1_id, "email", "Envio de proposta comercial")
    assert i2 is not None
    print(f"  [OK] Interacao adicionada: {i2['tipo']}")

    i3 = add_interaction(c2_id, "ligacao", "Discussao sobre parceria",
                         follow_up_necessario=True,
                         follow_up_descricao="Enviar contrato de parceria")
    assert i3 is not None
    print(f"  [OK] Interacao com follow-up adicionada")

    # Interacoes do contato
    ints = get_interactions_for_contact(c1_id)
    assert len(ints) == 2
    print(f"  [OK] Interacoes do contato: {len(ints)}")

    # Interacoes recentes
    recent = get_recent_interactions(10)
    assert len(recent) == 3
    print(f"  [OK] Interacoes recentes: {len(recent)}")

    # Follow-ups pendentes
    fups = get_pending_follow_ups()
    assert len(fups) == 1
    print(f"  [OK] Follow-ups pendentes: {len(fups)}")

    # Setup perfil
    profile = setup_profile("Teste User", "empresario")
    assert profile["tipo"] == "empresario"
    print(f"  [OK] Perfil configurado: {profile['tipo']}")

    # Stats
    stats = get_crm_stats()
    assert stats["total_contatos"] == 3
    assert stats["total_interacoes"] == 3
    print(f"  [OK] Stats: {stats['total_contatos']} contatos, {stats['total_interacoes']} interacoes")

    # Soft delete
    deleted = delete_contact(c3_id)
    assert deleted
    active = find_contacts()
    assert len(active) == 2
    print(f"  [OK] Soft delete: {len(active)} contatos ativos")

    print("  Todos os testes de storage OK!")
    return c1_id, c2_id


def test_tools(c1_id: str, c2_id: str):
    """Testa as ferramentas (tools) do CRM"""
    print("\n--- Testando Tools ---")

    # Contact Manager
    from tools.contact_manager import (
        crm_add_contact, crm_search_contacts, crm_get_contact_details,
        crm_update_contact, crm_register_interaction, crm_get_recent_activity,
        crm_get_follow_ups, crm_get_stats, crm_list_all_contacts
    )

    result = json.loads(crm_add_contact("Fernanda Lima", categoria="networking", empresa="StartupX"))
    assert result["status"] == "success"
    print(f"  [OK] crm_add_contact: {result['contato']['nome']}")

    result = json.loads(crm_search_contacts(nome="Ana"))
    assert result["total"] >= 1
    print(f"  [OK] crm_search_contacts: {result['total']} resultado(s)")

    result = json.loads(crm_get_contact_details(c1_id))
    assert result["status"] == "success"
    print(f"  [OK] crm_get_contact_details: {result['contato']['nome']}")

    result = json.loads(crm_update_contact(c1_id, notas="Cliente estrategico"))
    assert result["status"] == "success"
    print(f"  [OK] crm_update_contact")

    result = json.loads(crm_register_interaction(
        c2_id, "mensagem", "Alinhamento rapido por WhatsApp", sentimento="positivo"
    ))
    assert result["status"] == "success"
    print(f"  [OK] crm_register_interaction")

    result = json.loads(crm_get_recent_activity("5"))
    assert result["status"] == "success"
    print(f"  [OK] crm_get_recent_activity: {result['total']} interacoes")

    result = json.loads(crm_get_follow_ups())
    assert result["status"] == "success"
    print(f"  [OK] crm_get_follow_ups: {result['total']} pendentes")

    result = json.loads(crm_get_stats())
    assert result["status"] == "success"
    print(f"  [OK] crm_get_stats: {result['estatisticas']['total_contatos']} contatos")

    result = json.loads(crm_list_all_contacts())
    assert result["status"] == "success"
    print(f"  [OK] crm_list_all_contacts: {result['total']} contatos")

    # Relationship Scorer
    from tools.relationship_scorer import (
        crm_score_all_relationships, crm_score_contact, crm_get_neglected_contacts
    )

    result = json.loads(crm_score_all_relationships())
    assert result["status"] == "success"
    print(f"  [OK] crm_score_all_relationships: score medio={result['score_medio']}")

    result = json.loads(crm_score_contact(c1_id))
    assert result["status"] == "success"
    print(f"  [OK] crm_score_contact: {result['score']['score']}/100")

    result = json.loads(crm_get_neglected_contacts("0"))
    assert result["status"] == "success"
    print(f"  [OK] crm_get_neglected_contacts: {result['total_negligenciados']}")

    # Network Analyzer
    from tools.network_analyzer import (
        crm_analyze_network, crm_get_communication_suggestions, crm_get_relationship_report
    )

    result = json.loads(crm_analyze_network())
    assert result["status"] == "success"
    print(f"  [OK] crm_analyze_network: {result['resumo']['total_contatos']} contatos analisados")

    result = json.loads(crm_get_communication_suggestions())
    assert result["status"] == "success"
    print(f"  [OK] crm_get_communication_suggestions: {result['total_sugestoes']} sugestoes")

    result = json.loads(crm_get_relationship_report())
    assert result["status"] == "success"
    print(f"  [OK] crm_get_relationship_report: saude={result['relatorio']['metricas']['saude_geral_percentual']}%")

    # Profile Manager
    from tools.profile_manager import crm_get_profile, crm_list_profiles

    result = json.loads(crm_get_profile())
    assert result["status"] == "success"
    print(f"  [OK] crm_get_profile: {result['perfil']['tipo']}")

    result = json.loads(crm_list_profiles())
    assert result["status"] == "success"
    print(f"  [OK] crm_list_profiles: {len(result['perfis'])} perfis")

    print("  Todas as tools OK!")


def main():
    print("=" * 60)
    print("  TESTES DO CRM DE RELACIONAMENTOS")
    print("=" * 60)

    setup_test_env()

    try:
        test_models()
        test_profiles()
        c1_id, c2_id = test_storage()
        test_tools(c1_id, c2_id)

        print("\n" + "=" * 60)
        print("  TODOS OS TESTES PASSARAM!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n  [FALHA] Assertion error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [ERRO] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup_test_env()


if __name__ == "__main__":
    main()
