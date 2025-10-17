"""Точка входа"""

import asyncio

from langchain_core.runnables.schema import StreamEvent

from rich.console import Console
from rich.prompt import Prompt

from src.agents import tool_agent_executor

console = Console()

def pretty_print(event: StreamEvent) -> None:
    """Печатает событие из стрима

    Args:
        event: само событие.

    Returns:
        ничего не возвращает.
    """
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, flush=True, end="")

    elif event["event"] == "on_tool_start":
        name = event.get("name", "")
        msg = f"\n[magenta]=== Вызываю {name} ===[/magenta]"
        console.print(msg)
    elif event["event"] == "on_tool_end":
        name = event.get("name", "")
        msg = f"\n[green]=== Вызов {name} завершён ===[/green]"
        console.print(msg)

async def main():
    console.print(
        "[bold green]Помощник по расписанию[/bold green]"
    )
    console.print(
        "Нажмите Ctrl+C или Ctrl+D, чтобы выйти."
    )
    try:
        while True:
            query = Prompt.ask("[cyan]Ввод[/cyan]")

            async for event in tool_agent_executor.astream_events({
                "input": query
            }):
                pretty_print(event)

    except (KeyboardInterrupt, EOFError):
        console.print("\nПока!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:
        console.print(f"\n[bold red]Ошибка: {err}[/bold red]")
