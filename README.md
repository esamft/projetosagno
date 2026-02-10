# ObsidianAI

Agentes inteligentes para gestao de conhecimento no Obsidian. Analisa, organiza, conecta e facilita o acesso ao seu vault usando IA.

## Agentes

| Agente | Comando | O que faz |
|--------|---------|-----------|
| **Reviewer** | `review` | Auditoria completa de saude do vault (notas orfas, vazias, sem tags) |
| **Organizer** | `organize` | Sugere melhorias na estrutura de pastas e organizacao |
| **Linker** | `links` | Descobre conexoes faltantes e sugere `[[wiki-links]]` |
| **Tagger** | `tags` | Analisa, normaliza e sugere tags para suas notas |
| **Summarizer** | `summarize` | Cria resumos e Maps of Content (MOCs) sobre temas |
| **Retriever** | `ask` | Responde perguntas buscando nas suas notas |

## Setup

```bash
# 1. Clone e instale dependencias
pip install -r requirements.txt

# 2. Configure o .env
cp .env.example .env
# Edite .env com sua API key e caminho do vault

# 3. Pronto
python main.py --help
```

### Variaveis de ambiente

```
ANTHROPIC_API_KEY=sk-ant-...       # Sua chave da API Anthropic
OBSIDIAN_VAULT_PATH=/caminho/vault  # Caminho absoluto do seu vault
LLM_MODEL=claude-sonnet-4-5-20250929     # Modelo a usar
EXCLUDED_FOLDERS=.obsidian,.trash   # Pastas a ignorar
LANGUAGE=pt-br                      # Idioma das respostas
```

## Uso

### Estatisticas rapidas (sem LLM)

```bash
python main.py stats
python main.py stats --vault /outro/vault
```

### Auditoria do vault

```bash
python main.py review
```

### Sugestoes de organizacao

```bash
python main.py organize
python main.py organize --focus "pasta de projetos"
```

### Descobrir links faltantes

```bash
python main.py links
python main.py links --note "minha nota.md"
```

### Melhorar sistema de tags

```bash
python main.py tags
```

### Resumir um tema / criar MOC

```bash
python main.py summarize "machine learning"
python main.py summarize "projetos" --moc
```

### Perguntar sobre suas notas

```bash
python main.py ask "o que eu sei sobre Python async?"
python main.py ask "quais projetos estou trabalhando?"
```

### Modo chat interativo

```bash
python main.py chat
```

No chat, use:
- `/agentes` — listar agentes disponiveis
- `/agente <nome>` — trocar agente ativo
- `/sair` — encerrar

## Arquitetura

```
main.py                  # CLI (typer + rich)
config/settings.py       # Configuracoes via .env
vault/
  models.py              # Modelos Pydantic (Note, NoteMeta, VaultStats)
  parser.py              # Parser de markdown, frontmatter, wiki-links, tags
  reader.py              # Leitor do vault com indices e busca
tools/
  toolkit.py             # Registry de tools para os agentes
agents/
  base.py                # Base agent com loop de tool-use (Anthropic API)
  organizer.py           # Agente de organizacao
  linker.py              # Agente de links
  tagger.py              # Agente de tags
  summarizer.py          # Agente de resumos/MOCs
  reviewer.py            # Agente de auditoria
  retriever.py           # Agente de busca/perguntas
```

### Como funciona

1. O **VaultReader** carrega e indexa todas as notas `.md` do vault
2. O **VaultToolkit** expoe operacoes do vault como tools para a API Anthropic
3. Cada **agente** tem um system prompt especializado e um conjunto de tools
4. O **BaseAgent** executa o loop de tool-use: envia mensagem, executa tools, retorna resultado
5. A **CLI** orquestra tudo com interface rich no terminal

### Funcionalidades do parser

- Frontmatter YAML (tags, aliases, campos customizados)
- Wiki-links `[[nota]]` e `[[nota|alias]]`
- Tags inline `#tag` e hierarquicas `#area/subtema`
- Headings markdown
- Campos Dataview `campo:: valor`
- Resolucao de backlinks automatica
- Indice por titulo, alias e stem
