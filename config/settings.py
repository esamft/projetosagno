"""
Configurações centralizadas do projeto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).parent.parent
TOOLS_DIR = BASE_DIR / "tools"
AGENTS_DIR = BASE_DIR / "agents"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configurações de modelo
DEFAULT_MODEL = "gpt-4o"  # ou "gpt-4o-mini" para economia
TEMPERATURE = 0.7

# Configurações de log
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
