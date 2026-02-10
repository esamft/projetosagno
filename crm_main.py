"""
CRM de Relacionamentos Pessoal - Entry Point

Sistema de CRM pessoal com agentes inteligentes especializados
para mapeamento automatico de relacionamentos.

Modos de execucao:
  python crm_main.py                  -> Modo interativo (chat)
  python crm_main.py --setup          -> Configurar perfil
  python crm_main.py --report         -> Relatorio rapido
  python crm_main.py --suggest        -> Sugestoes de comunicacao
  python crm_main.py --agent <nome>   -> Usar agente especifico
"""
import sys
import argparse
from loguru import logger

from config.settings import OPENAI_API_KEY


def check_api_key():
    """Verifica se a API key esta configurada"""
    if not OPENAI_API_KEY:
        print("\n[ERRO] OPENAI_API_KEY nao configurada!")
        print("Configure no arquivo .env ou como variavel de ambiente.")
        print("Exemplo: export OPENAI_API_KEY='sk-...'")
        sys.exit(1)


def run_interactive(agent_name: str = "orchestrator"):
    """Executa o CRM em modo interativo (chat)"""
    from agents.crm_orchestrator import create_crm_orchestrator
    from agents.relationship_analyst import create_relationship_analyst
    from agents.communication_strategist import create_communication_strategist
    from agents.network_mapper import create_network_mapper
    from agents.priority_advisor import create_priority_advisor

    agents = {
        "orchestrator": ("Orquestrador CRM", create_crm_orchestrator),
        "analyst": ("Analista de Relacionamentos", create_relationship_analyst),
        "strategist": ("Estrategista de Comunicacao", create_communication_strategist),
        "mapper": ("Mapeador de Rede", create_network_mapper),
        "advisor": ("Consultor de Prioridades", create_priority_advisor),
    }

    if agent_name not in agents:
        print(f"\nAgente '{agent_name}' nao encontrado.")
        print(f"Agentes disponiveis: {', '.join(agents.keys())}")
        sys.exit(1)

    nome_agente, create_fn = agents[agent_name]

    print("\n" + "=" * 60)
    print("  CRM DE RELACIONAMENTOS PESSOAL")
    print(f"  Agente: {nome_agente}")
    print("=" * 60)
    print("\nDigite suas mensagens. Use 'sair' para encerrar.\n")

    agent = create_fn()

    while True:
        try:
            user_input = input("\nVoce: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("sair", "exit", "quit", "q"):
                print("\nAte logo! Cuide dos seus relacionamentos.")
                break

            print(f"\n[{nome_agente} pensando...]\n")
            response = agent.run(user_input)
            print(response.content)

        except KeyboardInterrupt:
            print("\n\nAte logo!")
            break
        except Exception as e:
            logger.error(f"Erro: {e}")
            print(f"\n[Erro] {e}")


def run_quick_report():
    """Gera um relatorio rapido sem modo interativo"""
    from tools.network_analyzer import crm_get_relationship_report
    from tools.relationship_scorer import crm_score_all_relationships
    from storage.crm_store import load_contacts

    contacts = load_contacts()
    if not contacts:
        print("\nCRM vazio. Adicione contatos primeiro.")
        print("Execute: python crm_main.py --setup")
        return

    print("\n" + "=" * 60)
    print("  RELATORIO RAPIDO - CRM DE RELACIONAMENTOS")
    print("=" * 60)

    import json

    print("\n--- SCORES DE RELACIONAMENTO ---\n")
    scores = json.loads(crm_score_all_relationships())
    if scores["status"] == "success":
        print(f"Total de contatos: {scores['total_contatos']}")
        print(f"Score medio: {scores['score_medio']}")
        print(f"Contatos criticos: {scores['contatos_criticos']}")
        print(f"Alertas: {scores['total_alertas']}")
        print()
        for s in scores["scores"][:10]:
            indicator = "!!" if s["prioridade"] == "critica" else ">>" if s["prioridade"] == "alta" else "--"
            print(f"  {indicator} {s['contato_nome']}: {s['score']}/100 ({s['forca']}) "
                  f"- {s['dias_sem_contato']}d sem contato")
            if s.get("alerta"):
                print(f"     ALERTA: {s['alerta']}")

    print("\n--- RELATORIO EXECUTIVO ---\n")
    report = json.loads(crm_get_relationship_report())
    if report["status"] == "success":
        r = report["relatorio"]
        print(r.get("resumo", ""))
        if r.get("plano_semanal"):
            print("\nPlano da semana:")
            for p in r["plano_semanal"][:5]:
                print(f"  -> {p['acao']}: {p['contato']} ({p['categoria']}) "
                      f"- {p['dias_sem_contato']}d atrasado")

    print("\n" + "=" * 60)


def run_suggestions():
    """Mostra sugestoes de comunicacao"""
    from tools.network_analyzer import crm_get_communication_suggestions
    from storage.crm_store import load_contacts

    contacts = load_contacts()
    if not contacts:
        print("\nCRM vazio. Adicione contatos primeiro.")
        return

    import json

    print("\n" + "=" * 60)
    print("  SUGESTOES DE COMUNICACAO")
    print("=" * 60)

    suggestions = json.loads(crm_get_communication_suggestions())
    if suggestions["status"] == "success":
        total = suggestions["total_sugestoes"]
        print(f"\n{total} contato(s) precisam de atencao:\n")

        for s in suggestions["sugestoes"][:10]:
            urgencia_icon = {
                "critica": "[!!!]",
                "alta": "[!! ]",
                "media": "[!  ]",
                "baixa": "[   ]",
            }
            icon = urgencia_icon.get(s["urgencia"], "[   ]")
            print(f"  {icon} {s['contato_nome']} ({s['categoria']})")
            print(f"       {s['motivo']}")
            print(f"       Sugestao: {s['tipo_comunicacao']}")
            if s.get("contexto"):
                print(f"       Contexto: {s['contexto']}")
            print()
    else:
        print("\nNao foi possivel gerar sugestoes.")

    print("=" * 60)


def run_setup():
    """Modo de setup interativo do perfil"""
    from tools.profile_manager import crm_list_profiles, crm_setup_profile
    from storage.crm_store import load_profile
    import json

    print("\n" + "=" * 60)
    print("  CONFIGURACAO DO CRM DE RELACIONAMENTOS")
    print("=" * 60)

    current = load_profile()
    if current:
        print(f"\nPerfil atual: {current.get('nome', '?')} ({current.get('tipo', '?')})")
        resp = input("Deseja reconfigurar? (s/n): ").strip().lower()
        if resp not in ("s", "sim", "y", "yes"):
            print("Mantendo perfil atual.")
            return

    profiles = json.loads(crm_list_profiles())
    print("\nPerfis disponiveis:\n")
    for p in profiles["perfis"]:
        print(f"  [{p['tipo']}]")
        print(f"    {p['descricao']}")
        print(f"    Foco: {p['foco']}")
        print()

    nome = input("Seu nome: ").strip()
    if not nome:
        print("Nome e obrigatorio.")
        return

    tipo = input("Tipo de perfil (empresario/diretor/servidor_publico/saude/custom): ").strip().lower()
    if tipo not in ("empresario", "diretor", "servidor_publico", "saude", "custom"):
        print("Tipo invalido. Usando 'custom'.")
        tipo = "custom"

    objetivos = input("Objetivos (separados por ;) ou ENTER para usar defaults: ").strip()

    result = json.loads(crm_setup_profile(nome, tipo, objetivos))
    if result["status"] == "success":
        print(f"\nPerfil configurado com sucesso!")
        print(f"  Nome: {nome}")
        print(f"  Tipo: {tipo}")
        print(f"  Objetivos: {len(result['perfil'].get('objetivos', []))}")
        print(f"  Categorias prioritarias: {len(result['perfil'].get('categorias_prioritarias', []))}")
        print("\nAgora voce pode usar o CRM: python crm_main.py")
    else:
        print(f"\nErro: {result.get('message', 'desconhecido')}")


def main():
    parser = argparse.ArgumentParser(
        description="CRM de Relacionamentos Pessoal com Agentes Inteligentes"
    )
    parser.add_argument(
        "--setup", action="store_true",
        help="Configurar perfil do usuario"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Gerar relatorio rapido"
    )
    parser.add_argument(
        "--suggest", action="store_true",
        help="Mostrar sugestoes de comunicacao"
    )
    parser.add_argument(
        "--agent", type=str, default="orchestrator",
        choices=["orchestrator", "analyst", "strategist", "mapper", "advisor"],
        help="Agente especifico para usar (padrao: orchestrator)"
    )
    parser.add_argument(
        "--no-check", action="store_true",
        help="Pular verificacao de API key (para modos sem LLM)"
    )

    args = parser.parse_args()

    if args.setup:
        run_setup()
    elif args.report:
        run_quick_report()
    elif args.suggest:
        run_suggestions()
    else:
        check_api_key()
        run_interactive(args.agent)


if __name__ == "__main__":
    main()
