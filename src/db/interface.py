"""Интерфейс для сервиса базы данных"""

from typing import Protocol
from .models import Subject, SubjectCriticality

class AsyncDatabaseService(Protocol):
    """Интерфейс сервиса базы данных"""

    async def increment_skips(
            self,
            subject_name: str,
            count: int = 1
    ) -> Subject:
        """Увеличивает количество пропусков предмета

        Args:
            subject_name: имя предмета.
            count: количество пропусков, на которое надо увеличить.

        Returns:
            только обновляет данные в БД.
        """

    async def decrement_skips(
            self,
            subject_name: str,
            count: int = 1
    ) -> Subject:
        """Уменьшает количество пропусков предмета

        Args:
            subject_name: имя предмета.
            count: количество пропусков, на которое надо уменьшить.

        Returns:
            только обновляет данные в БД.
        """

    async def add_subject(
            self,
            subject_name: str,
            skips: int = 0,
            criticality: SubjectCriticality = SubjectCriticality.MEDIUM
    ) -> Subject:
        """Создаёт в базе новый предмет, устанавливает количество пропусков

        Args:
            subject_name: название предмета.
            skips: изначальное количество пропусков.

        Returns:
            только создаёт запись в БД."""

    async def get_all(self) -> list[Subject]:
        """Возвращает все предметы из БД

        Returns:
            список всех предметов в базе данных.
        """
