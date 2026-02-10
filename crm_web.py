"""
CRM de Relacionamentos - Servidor Web

Inicia o servidor FastAPI com a interface web do CRM.

Uso:
  python crm_web.py              -> Inicia na porta 8000
  python crm_web.py --port 3000  -> Inicia na porta 3000
"""
import argparse
import sys
from pathlib import Path

# Garantir imports do projeto
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="CRM Web Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host (padrao: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Porta (padrao: 8000)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload em desenvolvimento")
    args = parser.parse_args()

    import uvicorn

    print(f"\n  CRM de Relacionamentos")
    print(f"  http://localhost:{args.port}\n")

    uvicorn.run(
        "web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
