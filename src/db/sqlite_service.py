"""БД сервис на SQLite"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from .models import Subject, SubjectCriticality
from .exceptions import InvalidCount, SubjectAlreadyExists, SubjectNotFound


class SqliteService:
    """Реализация сервиса БД на SQLite и SQLAlchemy"""

    def __init__(
        self,
        engine: AsyncEngine
    ):
        self.engine = engine
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

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

        if count <= 0:
            raise InvalidCount(f"Невозможно увеличить пропуски на {count}")

        async with self.session_factory() as session:
            stmt = select(Subject).where(Subject.name == subject_name)
            result = await session.execute(stmt)
            subject = result.scalar_one_or_none()

            if subject:
                subject.skips += count

                await session.commit()
                await session.refresh(subject)

                return subject

            else:
                raise SubjectNotFound(f"Не найден предмет {subject_name}")
            

    async def decrement_skips(self, subject_name: str, count: int = 1) -> Subject:
        """Уменьшает количество пропусков предмета

        Args:
            subject_name: имя предмета.
            count: количество пропусков, на которое надо уменьшить.

        Returns:
            только обновляет данные в БД.
        """
        if count <= 0:
            raise InvalidCount(f"Невозможно уменьшить пропуски на {count}")

        async with self.session_factory() as session:
            stmt = select(Subject).where(Subject.name == subject_name)
            result = await session.execute(stmt)
            subject = result.scalar_one_or_none()

            if subject:
                subject.skips -= count

                await session.commit()
                await session.refresh(subject)

                return subject

            else:
                raise SubjectNotFound(f"Не найден предмет {subject_name}")

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

        if skips < 0:
            raise InvalidCount(
                "Количество пропусков должно быть положительным числом"
            )

        async with self.session_factory() as session:
            stmt = select(Subject).where(Subject.name == subject_name)
            result = await session.execute(stmt)
            subject = result.scalar_one_or_none()

            if subject:
                raise SubjectAlreadyExists(
                    f"Предмет {subject_name} уже есть в базе данных"
                )

            new_subject = Subject(
                name=subject_name,
                skips=skips,
                criticality=criticality
            )

            session.add(new_subject)
            await session.commit()
            await session.refresh(new_subject)

            return new_subject

    async def get_all(self) -> list[Subject]:
        """Возвращает все предметы из БД

        Returns:
            список всех предметов в базе данных.
        """

        async with self.session_factory() as session:
            stmt = select(Subject)

            result = await session.execute(stmt)
            
            subjects = result.scalars().all()

            if not subjects:
                raise SubjectAlreadyExists("Не было найдено предметов")

            return list(subjects)
