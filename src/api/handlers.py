from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from langchain_core.runnables.schema import StreamEvent

from ..config import app_config
from ..ai import tool_agent_executor as agent

import logging

logger = logging.getLogger(__name__)
dp = Dispatcher()

def is_my_username(username: str) -> bool:
    """Проверка на то, что бот общается со мной

    Args:
        username: имя пользователя, которое нужно проверить.

    Returns:
        Мой ли это username.
    """
    return username == app_config.my_username

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

@dp.message(Command("help"))
async def help_command_handler(message: Message) -> None:
    logger.info("Help command triggered")

    msg = """Данный бот является ИИ-агентом для помощи в составлении расписания и умеет:
1. Получать и изменять мероприятия в Google Calendar (будьте аккуратны).
2. Работать с базой данных пропусков.

В базе данных есть сущность Subject, которая представляется полями:
- `name` - название предмета.
- `skips` - количество пропусков.
- `criticality` - критичность предмета: низкая, средняя или высокая.

Вы можете попросить агента добавить предмет, прибавить или убавить пропуски. 
"""
    await message.reply(msg)
    return

@dp.message()
async def message_handler(message: Message) -> None:
    """Обработчик всех сообщений"""
    logger.info("Received a message")
    if not (user := message.from_user):
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return

    if not user.username or not is_my_username(user.username):
        logger.warning("Unknown user")
        await message.reply("Незвестный пользователь")
        return

    logger.info("Sending message")
    sent_msg = await message.reply("Ответ:")

    logger.info("Invoking Agent")
    full_text = ""
    last_update_time = datetime.now().timestamp()
    update_interval = 0.5
    async for event in agent.astream_events(
        {"input": message.md_text}
    ):
        chunk = get_chunk(event)
        if not chunk:
            continue

        full_text += chunk

        current_time = datetime.now().timestamp()
        if current_time - last_update_time >= update_interval:
            try:
                await sent_msg.edit_text(full_text)
                last_update_time = current_time

            except Exception as err:
                logger.warning("Exception: %s", err)
                pass
    await sent_msg.edit_text(full_text)
