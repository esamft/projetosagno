# ObsidianAI

Agentes inteligentes para gestao de conhecimento no Obsidian. Analisa, organiza, conecta e facilita o acesso ao seu vault usando IA.

Dois modos de uso:
- **MCP Server** — conecta ao Claude Desktop / Claude Code para usar os agentes direto no chat
- **CLI** — interface no terminal com 6 agentes especializados

## Agentes

| Agente | Comando CLI | O que faz |
|--------|-------------|-----------|
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
```

### Variaveis de ambiente

```
ANTHROPIC_API_KEY=sk-ant-...       # Sua chave da API Anthropic
OBSIDIAN_VAULT_PATH=/caminho/vault  # Caminho absoluto do seu vault
LLM_MODEL=claude-sonnet-4-5-20250929     # Modelo a usar
EXCLUDED_FOLDERS=.obsidian,.trash   # Pastas a ignorar
```

---

## MCP Server (recomendado)

O MCP Server expoe seu vault como tools que o Claude pode usar diretamente. Ele permite **ler e escrever** no vault.

### Configurar no Claude Desktop

Edite o arquivo de configuracao do Claude Desktop:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "obsidian-ai": {
      "command": "python",
      "args": ["/caminho/completo/para/mcp_server.py"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/caminho/do/seu/vault"
      }
    }
  }
}
```

### Configurar no Claude Code

Adicione ao `.mcp.json` do projeto ou ao config global:

```json
{
  "mcpServers": {
    "obsidian-ai": {
      "command": "python",
      "args": ["/caminho/completo/para/mcp_server.py"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/caminho/do/seu/vault"
      }
    }
  }
}
```

### Tools disponiveis via MCP

**Leitura:**
| Tool | Descricao |
|------|-----------|
| `vault_stats` | Estatisticas gerais do vault |
| `search_notes` | Busca notas por conteudo ou titulo |
| `read_note` | Le conteudo completo de uma nota |
| `list_notes` | Lista todas as notas |
| `find_orphan_notes` | Notas sem links de entrada/saida |
| `find_notes_without_tags` | Notas sem tags |
| `list_all_tags` | Todas as tags com contagem |
| `find_notes_by_tag` | Notas com tag especifica |
| `find_empty_notes` | Notas vazias |
| `find_short_notes` | Notas curtas (<30 palavras) |
| `folder_structure` | Estrutura de pastas |
| `note_links` | Links de entrada/saida de uma nota |
| `find_similar_titles` | Possiveis duplicatas |
| `most_linked_notes` | Notas mais referenciadas |
| `reload_vault` | Recarrega vault apos mudancas externas |

**Escrita:**
| Tool | Descricao |
|------|-----------|
| `create_note` | Cria nova nota com frontmatter |
| `append_to_note` | Adiciona conteudo ao final |
| `add_tags_to_note` | Adiciona tags ao frontmatter |
| `remove_tags_from_note` | Remove tags |
| `insert_link_in_note` | Insere `[[wiki-link]]` |
| `update_note_content` | Substitui conteudo (mantendo frontmatter) |
| `update_frontmatter` | Atualiza campos do frontmatter |

### Prompts pre-definidos

O MCP server inclui prompts prontos que aparecem no Claude Desktop:

- **review_vault** — Auditoria completa da saude do vault
- **suggest_links** — Encontra conexoes faltantes
- **organize_tags** — Analisa e melhora sistema de tags
- **create_moc** — Cria Map of Content sobre um tema
- **daily_review** — Revisao diaria com sugestoes de acao

### Testar o MCP Server

```bash
# Testar localmente
python mcp_server.py
```

---

## CLI

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

---

## Arquitetura

```
mcp_server.py            # MCP Server (FastMCP) — modo principal
main.py                  # CLI (typer + rich) — modo alternativo
config/settings.py       # Configuracoes via .env
vault/
  models.py              # Modelos Pydantic (Note, NoteMeta, VaultStats)
  parser.py              # Parser de markdown, frontmatter, wiki-links, tags
  reader.py              # Leitor do vault com indices e busca
  writer.py              # Escritor — cria e modifica notas
tools/
  toolkit.py             # Registry de tools para os agentes CLI
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

**Modo MCP:**
1. O `mcp_server.py` inicia como MCP Server via stdio
2. Claude Desktop/Code conecta e recebe a lista de tools
3. Quando voce conversa com Claude, ele chama as tools para ler/escrever no vault
4. O vault e acessado diretamente pelo filesystem (sem precisar do Obsidian aberto)

**Modo CLI:**
1. O `VaultReader` carrega e indexa todas as notas `.md` do vault
2. O `VaultToolkit` expoe operacoes como tools para a API Anthropic
3. Cada agente tem um system prompt especializado e um conjunto de tools
4. O `BaseAgent` executa o loop de tool-use
5. A CLI orquestra tudo com interface rich no terminal

### Funcionalidades do parser

- Frontmatter YAML (tags, aliases, campos customizados)
- Wiki-links `[[nota]]` e `[[nota|alias]]`
- Tags inline `#tag` e hierarquicas `#area/subtema`
- Headings markdown
- Campos Dataview `campo:: valor`
- Resolucao de backlinks automatica
- Indice por titulo, alias e stem
