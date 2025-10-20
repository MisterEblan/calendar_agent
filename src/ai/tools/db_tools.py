
from langchain_core.tools import tool

from ...db import (
    engine,
    SubjectNotFound,
    InvalidCount,
    SubjectAlreadyExists,
    SqliteService,
    SubjectCriticality
)
from ...helpers.context_builder import ContextBuilder


@tool
async def get_subjects_skips() -> str:
    """Получает пропуски по предметам из базы данных

    Returns:
        Строки формата
        `[Название предмета] ([Критичность предмета]): [Количество пропусков]`
    """
    service = SqliteService(engine)

    try:
        subjects = await service.get_all()

        return ContextBuilder.from_subjects(subjects)
    except SubjectNotFound:
        return "Нет данных о предметах"
    except Exception as err:
        return f"Ошибка при получении информации: {err}"

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
            subject_name=subject_name,
            skips=skips,
            criticality=criticality
        )

        return f"Предмет {subject_name} добавлен"

    except SubjectAlreadyExists:
        return "Предмет уже существует"
    except Exception as err:
        return f"Ошибка при получении информации: {err}"

db_tools = [
    get_subjects_skips,
    increment_skips,
    decrement_skips,
    create_subject
]
