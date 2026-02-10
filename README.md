# ObsidianAI — Zettelkasten Inteligente

Sistema de gestao de conhecimento pessoal baseado no metodo **Zettelkasten** com agentes IA integrados ao **Obsidian**. Organiza o que voce ja sabe, o que precisa saber e o que precisa fazer.

Dois modos de uso:
- **MCP Server** — conecta ao Claude Desktop / Claude Code para usar direto no chat
- **CLI** — interface no terminal com 10 agentes especializados

## Metodo Zettelkasten

O sistema segue a estrutura Zettelkasten com pastas por tipo de nota:

```
vault/
  inbox/        -> Fleeting notes (capturas rapidas, processar em 24-48h)
  zettel/       -> Permanent notes (uma ideia atomica por nota)
  references/   -> Literature notes (resumos de fontes externas)
  structure/    -> Structure notes / MOCs (indices tematicos)
  projects/     -> Project notes (acoes e entregas ativas)
  people/       -> Person/meeting notes (contatos, reunioes, CRM)
  archive/      -> Material concluido ou inativo
  templates/    -> Templates de notas
```

### Fluxo Zettelkasten

```
Pensamento -> inbox/ (fleeting) -> zettel/ (permanent) -> structure/ (MOC)
                                -> references/ (se for de fonte)
                                -> projects/ (se for acao)
```

### Frontmatter padrao

```yaml
---
title: Titulo da nota
type: zettel        # fleeting | zettel | literature | structure | project
tags: [tema, subtema]
created: 2026-02-10
source: ""          # para literature notes
---
```

## Agentes

| Agente | Comando CLI | O que faz |
|--------|-------------|-----------|
| **Zettel** | `zettel` | Processa inbox, verifica atomicidade, mantem o sistema |
| **Capture** | `capture` | Captura rapida de pensamentos, fontes e acoes |
| **Reviewer** | `review` | Auditoria Zettelkasten (fluxo, atomicidade, conexoes, cobertura) |
| **Organizer** | `organize` | Reorganiza vault para a estrutura Zettelkasten |
| **Linker** | `links` | Tece conexoes intelectuais faltantes entre notas |
| **Tagger** | `tags` | Normaliza e sugere tags seguindo taxonomia Zettelkasten |
| **Summarizer** | `summarize` | Cria Structure Notes (MOCs) sobre temas |
| **Retriever** | `ask` | Navega o grafo de conhecimento para responder perguntas |
| **Ingest** | `ingest` | Processa PDFs, imagens e textos em notas Zettelkasten com aprovacao |
| **Scout** | `scout` | Busca novidades na web sobre seus temas e propoe notas |

## Setup

```bash
# 1. Instale dependencias
pip install -r requirements.txt

# 2. Configure o .env
cp .env.example .env
# Edite com sua API key e caminho do vault

# 3. (Opcional) Crie a estrutura Zettelkasten
# Via MCP: use a tool setup_zettelkasten
# Via CLI: python main.py zettel --action setup
```

---

## MCP Server (recomendado)

O MCP Server expoe o vault como tools para o Claude usar diretamente.

### Configurar no Claude Desktop

Edite `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) ou `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

### Tools MCP

**Leitura (15):**

| Tool | Descricao |
|------|-----------|
| `vault_stats` | Estatisticas gerais do vault |
| `search_notes` | Busca notas por conteudo ou titulo |
| `read_note` | Le conteudo completo de uma nota |
| `list_notes` | Lista todas as notas |
| `find_orphan_notes` | Notas sem links |
| `find_notes_without_tags` | Notas sem tags |
| `list_all_tags` | Tags com contagem |
| `find_notes_by_tag` | Notas com tag especifica |
| `find_empty_notes` | Notas vazias |
| `find_short_notes` | Notas curtas |
| `folder_structure` | Estrutura de pastas |
| `note_links` | Links de uma nota |
| `find_similar_titles` | Possiveis duplicatas |
| `most_linked_notes` | Notas mais referenciadas |
| `reload_vault` | Recarrega vault |

**Zettelkasten (6):**

| Tool | Descricao |
|------|-----------|
| `inbox_notes` | Fleeting notes na inbox para processar |
| `notes_by_type` | Filtra por tipo (fleeting, zettel, literature, structure, project) |
| `notes_by_folder` | Notas de uma pasta especifica |
| `find_non_atomic_notes` | Permanent notes longas que violam atomicidade |
| `setup_zettelkasten` | Cria estrutura de pastas Zettelkasten |
| `move_note` | Move nota entre pastas |

**Busca Web (3):**

| Tool | Descricao |
|------|-----------|
| `web_search_news` | Busca noticias recentes na web sobre um tema |
| `web_search_general` | Busca geral na web (artigos, blogs, docs) |
| `web_fetch_article` | Extrai conteudo principal de uma URL |

**Ingestao (2):**

| Tool | Descricao |
|------|-----------|
| `read_file_for_ingest` | Le arquivo externo (PDF, texto, imagem) e extrai conteudo |
| `ingest_raw_text` | Processa texto bruto colado para ingestao |

**Escrita (7):**

| Tool | Descricao |
|------|-----------|
| `create_note` | Cria nota com frontmatter |
| `append_to_note` | Adiciona conteudo ao final |
| `add_tags_to_note` | Adiciona tags |
| `remove_tags_from_note` | Remove tags |
| `insert_link_in_note` | Insere `[[wiki-link]]` |
| `update_note_content` | Substitui conteudo |
| `update_frontmatter` | Atualiza frontmatter |

### Prompts MCP

Aparecem como opcoes no Claude Desktop:

- **review_vault** — Auditoria Zettelkasten completa
- **process_inbox** — Processa fleeting notes da inbox
- **suggest_links** — Tece conexoes faltantes
- **organize_tags** — Normaliza sistema de tags
- **create_structure_note** — Cria Structure Note sobre um tema
- **daily_review** — Revisao diaria com foco em inbox
- **capture_thought** — Captura rapida de um pensamento
- **scout_news** — Busca novidades na web sobre um tema e propoe notas
- **ingest_file** — Processa arquivo externo e propoe notas Zettelkasten
- **ingest_text** — Processa texto colado e propoe notas Zettelkasten

---

## CLI

### Captura rapida

```bash
python main.py capture "Python generators sao lazy iterators"
python main.py capture "Ler livro Atomic Habits" --type project
```

### Buscar novidades na web (Scout)

```bash
# Buscar novidades sobre um tema
python main.py scout "inteligencia artificial"

# Buscar apenas noticias recentes
python main.py scout "Python 3.13" --news
```

### Ingerir dados brutos

```bash
# Ingerir um PDF (decompoem em notas atomicas)
python main.py ingest ~/Downloads/artigo-cientifico.pdf

# Ingerir texto bruto
python main.py ingest "Reuniao com Joao: discutimos arquitetura de microservicos..." --raw

# Ingerir com nome da fonte
python main.py ingest "Notas do livro cap 5..." --raw --source-name "Atomic Habits - Cap 5"
```

### Processar inbox

```bash
python main.py inbox
```

### Manutencao Zettelkasten

```bash
python main.py zettel --action review      # revisao do sistema
python main.py zettel --action atomicity   # verificar atomicidade
python main.py zettel --action setup       # verificar/criar estrutura
```

### Auditoria

```bash
python main.py review
```

### Estatisticas (sem LLM)

```bash
python main.py stats
```

### Organizacao

```bash
python main.py organize
python main.py organize --focus "pasta de projetos"
```

### Links faltantes

```bash
python main.py links
```

### Tags

```bash
python main.py tags
```

### Structure Notes / MOCs

```bash
python main.py summarize "machine learning" --moc
python main.py summarize "projetos"
```

### Perguntar sobre suas notas

```bash
python main.py ask "o que eu sei sobre Python async?"
```

### Chat interativo

```bash
python main.py chat
```

No chat: `/agentes` lista todos, `/agente zettel` troca agente, `/sair` encerra.

---

## Arquitetura

```
mcp_server.py            # MCP Server (FastMCP) — 33 tools, 10 prompts
main.py                  # CLI (typer + rich) — 13 comandos
config/settings.py       # Configuracoes via .env
vault/
  models.py              # Note, NoteMeta, VaultStats (Pydantic)
  parser.py              # Frontmatter, wiki-links, tags, Dataview
  reader.py              # Leitor com indices, busca, backlinks
  writer.py              # Cria, modifica, move notas
  ingest.py              # Extrator de conteudo (PDF, imagem, texto)
  web.py                 # Busca web (DuckDuckGo) e extracao de artigos
tools/
  toolkit.py             # 24 tools para agentes CLI
agents/
  base.py                # Loop de tool-use (Anthropic API)
  zettel.py              # Especialista Zettelkasten
  capture.py             # Captura rapida
  ingest.py              # Ingestao de dados brutos com validacao
  scout.py               # Busca novidades na web e atomiza
  organizer.py           # Organizacao estrutural
  linker.py              # Conexoes entre notas
  tagger.py              # Taxonomia de tags
  summarizer.py          # Structure Notes / MOCs
  reviewer.py            # Auditoria de saude
  retriever.py           # Busca e perguntas
```
