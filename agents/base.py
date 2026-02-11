"""Base agent com loop de tool-use via Anthropic API."""

from __future__ import annotations

from typing import Any, Callable

import anthropic

from config.settings import settings


class BaseAgent:
    """Agente base que integra com a API Anthropic usando tool-use."""

    name: str = "base"
    description: str = ""
    system_prompt: str = ""
    tool_names: list[str] = []

    def __init__(
        self,
        tools: list[dict],
        tool_handlers: dict[str, Callable],
    ):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        self.tools = tools
        self.tool_handlers = tool_handlers
        self.messages: list[dict[str, Any]] = []
        self._tool_calls_log: list[dict] = []

    def run(self, user_message: str, on_tool_call: Callable | None = None) -> str:
        """Executa o agente com uma mensagem do usuário.

        Args:
            user_message: Mensagem/pergunta do usuário.
            on_tool_call: Callback opcional chamado a cada tool call (nome, input, resultado).

        Returns:
            Resposta final do agente em texto.
        """
        self.messages = [{"role": "user", "content": user_message}]
        self._tool_calls_log.clear()
        return self._loop(on_tool_call)

    def continue_run(self, user_message: str, on_tool_call: Callable | None = None) -> str:
        """Continua a conversa mantendo o histórico anterior.

        Usado para fluxos de aprovação: o agente propõe, o usuário aprova,
        e o agente continua de onde parou.
        """
        self.messages.append({"role": "user", "content": user_message})
        return self._loop(on_tool_call)

    def _loop(self, on_tool_call: Callable | None = None) -> str:
        """Loop interno de tool-use."""

        for _ in range(20):  # limite de iterações de segurança
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.messages,
            )

            tool_uses = [b for b in response.content if b.type == "tool_use"]

            if not tool_uses:
                text_blocks = [b.text for b in response.content if hasattr(b, "text")]
                return "\n".join(text_blocks)

            self.messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:
                handler = self.tool_handlers.get(tool_use.name)
                if handler:
                    try:
                        result = handler(**tool_use.input)
                    except Exception as e:
                        result = f"Erro ao executar {tool_use.name}: {e}"
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(result),
                            "is_error": True,
                        })
                        self._tool_calls_log.append({
                            "tool": tool_use.name,
                            "input": tool_use.input,
                            "error": str(e),
                        })
                        if on_tool_call:
                            on_tool_call(tool_use.name, tool_use.input, f"ERRO: {e}")
                        continue

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(result),
                    })
                    self._tool_calls_log.append({
                        "tool": tool_use.name,
                        "input": tool_use.input,
                        "result_size": len(str(result)),
                    })
                    if on_tool_call:
                        on_tool_call(tool_use.name, tool_use.input, result)

            self.messages.append({"role": "user", "content": tool_results})

        return "Limite de iterações atingido. Tente uma pergunta mais específica."

    @property
    def tool_calls(self) -> list[dict]:
        return self._tool_calls_log
