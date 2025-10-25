"""Обработчики телеграм-бота"""

from datetime import datetime

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.filters import Command, StateFilter


from ..helpers import AgentManager, get_chunk
from ..auth.google_auth_service import GoogleAuthService
from ..config import sample_messages 
from ..db import (
    SqliteService,
    engine
)

import logging

logger = logging.getLogger(__name__)
agent_manager = AgentManager()
dp = Dispatcher()

class AuthStates(StatesGroup):
    waiting_code = State()

@dp.message(Command("start"))
async def start_command_handler(message: Message) -> None:
    """Обработчик команды /start"""

    logger.info("Start command triggered")
    msg = sample_messages["start"]

    await message.reply(
        msg, parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def help_command_handler(message: Message) -> None:
    """Обработчики команды /help

    Присылает информацию по работе с ботом.
    """
    logger.info("Help command triggered")

    msg = sample_messages["help"]
    await message.reply(msg, parse_mode="Markdown")
    return

@dp.message(Command("auth"))
async def auth_handler(message: Message, state: FSMContext):
    """Обработчик команды /auth

    Создаёт пользователя в базе данных и присылает
    ссылку для аутентификации.
    """
    if not (user := message.from_user) or not user.username:
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return
    db_service = SqliteService(engine)

    try:
        db_user = await db_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username
        )

        auth_service = GoogleAuthService()

        auth_url = auth_service.get_authorization_url(str(db_user.id))

        msg = (
            "Для аутентификации перейдите по ссылке и отправьте код, "
            f"полученный от Google:\n{auth_url}"
        )

        await message.reply(
            "".join(msg), parse_mode=None
        )

        await state.set_state(AuthStates.waiting_code)
    except Exception as err: # pylint: disable=W0718
        logger.error("Authorization error: %s", err)
        await message.reply(
            "*Произошла ошибка при обработке сообщения*",
            parse_mode="Markdown"
        )

@dp.message(StateFilter(AuthStates.waiting_code))
async def auth_code_handler(message: Message, state: FSMContext) -> None:
    """Обработчик получения кода

    Смотрит на состояние бота и принимает код из OAuth2.0,
    который обменивается на токен.
    """
    if not (user := message.from_user) or not user.username:
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return
    if not message.text:
        message.reply("Не найден код в сообщении!")
        return

    auth_service = GoogleAuthService()
    db_service = SqliteService(engine)

    db_user = await db_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=user.username
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

@dp.message(Command("refresh"))
async def refresh_command_handler(message: Message) -> None:
    """Пересоздание агента"""
    if not (user := message.from_user) or not user.username:
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return

    try:
        db_service = SqliteService(engine)
        user_id = user.id

        db_user = await db_service.get_or_create_user(
            telegram_id=user_id,
            username=user.username
        )

        await agent_manager.create_agent_for_user(
            user_id=db_user.id,
            force=True
        )
        logger.info("Agent recreated")

        await message.reply("Агент был пересоздан")
    except Exception as err: # pylint: disable=W0718
        logger.error("Error with recreating agent: %s", err)
        message.reply("Произошла ошибка")

@dp.message()
async def message_handler(message: Message) -> None:
    """Обработчик всех сообщений

    Для каждого пользователя создаётся свой агент
    для работы с разными календарями.
    """
    logger.info("Received a message")
    if not (user := message.from_user) or not user.username:
        logger.warning("Unknown user")
        await message.reply("Неизвестный пользователь")
        return

    try:
        db_service = SqliteService(engine)
        user_id = user.id

        db_user = await db_service.get_or_create_user(
            telegram_id=user_id,
            username=user.username
        )

        agent = await agent_manager.create_agent_for_user(
            user_id=db_user.id
        )

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
    except Exception as err: # pylint: disable=W0718
        logger.error("Exception: %s", err)
        message.reply("Произошла ошибка")
