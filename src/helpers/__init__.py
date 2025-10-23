"""Вспомогательные классы"""

import logging
from langchain_core.runnables.schema import StreamEvent
from .agent_manager import AgentManager
from .context_builder import ContextBuilder

logger = logging.getLogger(__name__)

def get_chunk(event: StreamEvent) -> str | None:
    """Получает из события определённый чанк

    Args:
        event: событие стрима агента.

    Returns:
        определённый чанк текста, исходя из типа события
        или ничего.
    """
    if event["event"] == "on_chat_model_stream":
        return event["data"]["chunk"].content
    elif event["event"] == "on_tool_start":
        name = event["name"]

        logger.info("Agent Calling %s", name)
        logger.info("Input: %s", event["data"]["input"])

        return f"`<Вызов {name}>`"
    elif event["event"] == "on_tool_end":
        name = event["name"]

        logger.info("Called ended for %s", name)

        return f"\n`<Вызов {name} завершён>`\n"


__all__ = [
    "AgentManager",
    "ContextBuilder",
    "get_chunk"
]
