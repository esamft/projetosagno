"""
Entry point interativo para a Equipe de Planejamento de Slides

Modos de execucao:
    1. Interativo (padrao): Dialogo continuo com a equipe
    2. Single query: Passa uma query e recebe o plano completo
    3. Demo: Executa com uma query de exemplo

Uso:
    python slides_main.py                  # Modo interativo
    python slides_main.py --demo           # Modo demonstracao
    python slides_main.py --query "..."    # Query unica
"""
import sys
import argparse
from loguru import logger
from agents.slide_team import create_slide_planning_team


def run_interactive():
    """Modo interativo: dialogo continuo com a equipe."""
    print("\n" + "=" * 70)
    print("  EQUIPE DE PLANEJAMENTO DE SLIDES")
    print("  5 especialistas prontos para ajudar")
    print("=" * 70)
    print()
    print("Membros da equipe:")
    print("  1. Estrategista de Apresentacao")
    print("  2. Arquiteto de Conteudo")
    print("  3. Designer Visual")
    print("  4. Copywriter de Apresentacoes")
    print("  5. Revisor de Qualidade")
    print()
    print("Descreva sua apresentacao e a equipe vai trabalhar para voce.")
    print("Digite 'sair' para encerrar.\n")

    team = create_slide_planning_team()

    while True:
        try:
            user_input = input("\nVoce: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAte a proxima!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("sair", "exit", "quit", "q"):
            print("\nAte a proxima!")
            break

        print()
        team.print_response(user_input)


def run_single_query(query: str):
    """Modo query unica: processa e retorna resultado."""
    team = create_slide_planning_team()

    print("\n" + "=" * 70)
    print("QUERY:", query)
    print("=" * 70 + "\n")

    team.print_response(query)


def run_demo():
    """Modo demonstracao com query de exemplo."""
    demo_query = (
        "Preciso criar uma apresentacao de 20 minutos para um pitch "
        "de investimento da minha startup de IA. O publico sao investidores "
        "anjo e VCs. Temos 50 clientes, MRR de R$200k e crescemos 30% ao mes. "
        "Nossas cores sao azul (#1a73e8) e cinza (#5f6368)."
    )

    print("\n" + "=" * 70)
    print("  MODO DEMONSTRACAO")
    print("=" * 70)

    run_single_query(demo_query)


def main():
    parser = argparse.ArgumentParser(
        description="Equipe de Planejamento de Slides - Agno Framework"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Executa em modo demonstracao com query de exemplo",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Executa uma query unica e retorna o resultado",
    )

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.query:
        run_single_query(args.query)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
