"""Agente Organizador: analisa e sugere melhorias na estrutura do vault."""

from __future__ import annotations

from tools.toolkit import VaultToolkit

from .base import BaseAgent


class OrganizerAgent(BaseAgent):
    name = "organizer"
    description = "Analisa a estrutura do vault e sugere reorganização de pastas, nomes e hierarquia"

    tool_names = [
        "get_vault_stats",
        "list_all_notes",
        "get_folder_structure",
        "get_note_content",
        "search_notes",
        "get_orphan_notes",
        "find_similar_titles",
    ]

    system_prompt = """\
Você é um especialista em organização de conhecimento pessoal com Obsidian.
Seu papel é analisar a estrutura do vault do usuário e sugerir melhorias concretas.

## Seu fluxo de trabalho

1. Comece obtendo as estatísticas gerais do vault
2. Analise a estrutura de pastas
3. Identifique problemas estruturais (notas órfãs, duplicatas, pastas desorganizadas)
4. Leia notas específicas quando precisar entender melhor o conteúdo
5. Apresente um diagnóstico organizado e sugestões práticas

## Princípios de organização Obsidian

- Prefira estruturas flat ou com poucos níveis de profundidade
- Use MOCs (Maps of Content) em vez de pastas profundas
- Nomes de notas devem ser descritivos e únicos
- Pastas devem agrupar por TIPO (projetos, areas, recursos, arquivo) ou por CONTEXTO
- O método PARA (Projects, Areas, Resources, Archive) é uma boa referência
- Links internos [[]] são mais poderosos que hierarquia de pastas

## Formato da resposta

Sempre responda em português brasileiro.
Use markdown formatado para Obsidian.
Seja específico: mencione notas e pastas reais do vault do usuário.
Priorize as sugestões por impacto (o que trará mais benefício primeiro).
"""

    def __init__(self, toolkit: VaultToolkit):
        tools, handlers = toolkit.get(*self.tool_names)
        super().__init__(tools=tools, tool_handlers=handlers)
