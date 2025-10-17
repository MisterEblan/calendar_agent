"""Точка входа"""

import asyncio

from langchain_core._api import LangChainDeprecationWarning
from langchain_core.runnables.schema import StreamEvent

from src.agents import tool_agent_executor

import warnings
import colorama

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

colorama.init()

def pretty_print(event: StreamEvent) -> None:
    """Печатает событие из стрима

    Args:
        event: само событие.

    Returns:
        ничего не возвращает.
    """
    cyan = colorama.Fore.CYAN
    magenta = colorama.Fore.MAGENTA
    reset = colorama.Fore.RESET

    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, flush=True, end="")

    elif event["event"] == "on_tool_start":
        name = event.get("name", "")
        msg = f"\n{magenta}=== Вызываю {name} ==={reset}"
        print(msg)
    elif event["event"] == "on_tool_end":
        name = event.get("name", "")
        msg = f"\n{cyan}=== Вызов {name} завершён ==={reset}"
        print(f"\nВызов {name} завершён")

# query = "Привет! Какие у меня мероприятия будут дальше на сегодняшний день?"
async def main():
    try:
        while True:
            query = input("\nВвод >>> ")
            async for event in tool_agent_executor.astream_events({
                "input": query
            }):
                pretty_print(event)

    except (KeyboardInterrupt, EOFError):
        print("\nПока!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:
        print("Ошибка:", err)
