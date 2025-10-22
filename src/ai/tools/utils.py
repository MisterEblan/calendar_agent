import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from langchain.agents import tool
from langchain_core.tools import BaseTool
from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import (
    build_calendar_service,
)

from ...db import (
    engine,
    InvalidCount,
    SubjectNotFound,
    SubjectAlreadyExists,
    SubjectCriticality,
    SqliteService
)
from ...helpers.context_builder import ContextBuilder

import logging

logger = logging.getLogger(__name__)

def create_user_tools(user_id: int) -> list[BaseTool]:

    @tool
    async def get_subjects_skips() -> str:
        """Получает пропуски по предметам из базы данных

        Returns:
            Строки формата
            `[Название предмета] ([Критичность предмета]): [Количество пропусков]`
        """
        service = SqliteService(engine)

        try:
            subjects = await service.get_all(user_id=user_id)

            return ContextBuilder.from_subjects(subjects)
        except SubjectNotFound:
            msg =  "Нет данных о предметах"
            logger.error(msg)
            return msg
        except Exception as err:
            msg = f"Ошибка при получении информации: {err}"
            logger.error(msg)
            return msg

    @tool
    async def increment_skips(
            subject_name: str,
            count: int = 1
    ) -> str:
        """Увеличивает количество пропусков

        Args:
            subject_name: название предмета.
            count: число пропусков, на которое нужно увеличить.

        Returns:
            сообщение о результате.
        """

        service = SqliteService(engine)

        try:
            await service.increment_skips(
                user_id=user_id,
                subject_name=subject_name,
                count=count
        )
        
            return f"Пропуски для {subject_name} увеличины на {count}"

        except SubjectNotFound:
            return f"Не найден предмет {subject_name}"
        except InvalidCount as err:
            return f"Ошибка увеличения: {err}"
        except Exception:
            return "Неизвестная ошибка"

    @tool
    async def decrement_skips(
            subject_name: str,
            count: int = 1
    ) -> str:
        """Уменьшает количество пропусков

        Args:
            subject_name: название предмета.
            count: число пропусков, на которое нужно уменьшить.

        Returns:
            сообщение о результате.
        """

        service = SqliteService(engine)

        try:
            await service.decrement_skips(
                user_id=user_id,
                subject_name=subject_name,
                count=count
        )
        
            return f"Пропуски для {subject_name} уменьшены на {count}"

        except SubjectNotFound:
            return f"Не найден предмет {subject_name}"
        except InvalidCount as err:
            return f"Ошибка уменьшения: {err}"
        except Exception:
            return "Неизвестная ошибка"

    @tool
    async def create_subject(
        subject_name: str,
        skips: int = 0,
        criticality: SubjectCriticality = SubjectCriticality.MEDIUM
    ):
        """Создаёт в базе новый предмет, устанавливает количество пропусков

            Args:
                subject_name: название предмета.
                skips: изначальное количество пропусков.
                criticality: критичность предмета.
                    Одно из перечисленного:
                    - "низкая критичность"
                    - "средняя критичность"
                    - "высокая критичность"

            Returns:
                сообщение о результате.
            """

        service = SqliteService(engine)

        try:
            await service.add_subject(
                user_id=user_id,
                subject_name=subject_name,
                skips=skips,
                criticality=criticality
            )

            return f"Предмет {subject_name} добавлен"

        except SubjectAlreadyExists:
            return "Предмет уже существует"
        except Exception as err:
            return f"Ошибка при получении информации: {err}"

    return [
        get_subjects_skips,
        increment_skips,
        decrement_skips,
        create_subject
    ]

async def create_calendar_tools(user_id) -> list[BaseTool]:
    service = SqliteService(engine)

    token_data = await service.get_user_token(user_id)

    if not token_data:
        return []

    try:
        creds = Credentials.from_authorized_user_info(
            json.loads(token_data),
        scopes=[
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
    )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

            await service.save_user_token(user_id, creds.to_json())

        api_resource = build_calendar_service(creds)
        toolkit = CalendarToolkit(api_resource=api_resource)

        return toolkit.get_tools()
    except Exception as err:
        logger.error(
            "Ошибка при создании инструментов календаря: %s",
            err
        )
        return []
