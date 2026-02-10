import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", ""))
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
        self.EXCLUDED_FOLDERS = os.getenv(
            "EXCLUDED_FOLDERS", ".obsidian,.trash,.git,_templates"
        ).split(",")
        self.NOTE_EXTENSIONS = [".md"]
        self.LANGUAGE = os.getenv("LANGUAGE", "pt-br")

    def validate(self):
        errors = []
        if not self.VAULT_PATH or not self.VAULT_PATH.exists():
            errors.append(
                f"OBSIDIAN_VAULT_PATH inválido ou não encontrado: {self.VAULT_PATH}"
            )
        if self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY não configurada")
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY não configurada")
        return errors


settings = Settings()
