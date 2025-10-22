"""Обработчики телеграм-бота"""

from datetime import datetime

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.filters import Command, StateFilter

from langchain_core.runnables.schema import StreamEvent

from ..helpers.agent_manager import AgentManager

from ..auth.google_auth_service import GoogleAuthService

from ..db import (
    SqliteService,
    engine
)

from ..config import app_config

import logging

logger = logging.getLogger(__name__)
agent_manager = AgentManager()
dp = Dispatcher()

class AuthStates(StatesGroup):
    waiting_code = State()

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

    msg = """Данный бот является ИИ-агентом для помощи в составлении расписания.
Умеет:
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

@dp.message(Command("auth"))
async def auth_handler(message: Message, state: FSMContext):
    if not (user := message.from_user) or not user.username:
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return
    db_service = SqliteService(engine)
    db_user = await db_service.get_or_create_user(
        telegram_id=user.id,
        username=user.username
    )

    auth_service = GoogleAuthService()

    auth_url = auth_service.get_authorization_url(str(db_user.id))

    await message.reply(
        f"Для аутентификации перейдите по ссылке:\n`{auth_url}`"
    )

    await state.set_state(AuthStates.waiting_code)

@dp.message(StateFilter(AuthStates.waiting_code))
async def auth_code_handler(message: Message, state: FSMContext):
    auth_service = GoogleAuthService()
    db_service = SqliteService(engine)

    db_user = await db_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    code = message.text.strip()

    try:
        token_data = auth_service.exchange_code_for_token(
            code=code, user_id=str(db_user.id)
        )

        await db_service.save_user_token(
            user_id=db_user.id,
            token_data=token_data.to_json()
        )

        await message.reply("Аутентификация завершена!")
        await state.clear()
    except Exception as err: # pylint: disable=W0718
        await message.reply(f"Ошибка: {err}")

@dp.message()
async def message_handler(message: Message) -> None:
    """Обработчик всех сообщений"""
    logger.info("Received a message")
    if not (user := message.from_user) or not user.username:
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return

    db_service = SqliteService(engine)
    user_id = user.id

    db_user = await db_service.get_or_create_user(
        telegram_id=user_id,
        username=user.username
    )

    agent = await agent_manager.create_agent_for_user(user_id=db_user.id)

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
            except Exception as err: # pylint: disable=W0718
                logger.warning("Exception: %s", err)
                pass

    await sent_msg.edit_text(full_text)
