"""БД сервис на SQLite"""

from sqlalchemy import delete, select, and_
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from .models import Subject, SubjectCriticality, User, UserToken
from .exceptions import InvalidCount, SubjectAlreadyExists, SubjectNotFound

import logging

logger = logging.getLogger(__name__)


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

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str
    ) -> User:
        async with self.session_factory() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                logger.info("Пользователь %s не найден", username)
                user = User(
                    telegram_id=telegram_id,
                    username=username
                )
                session.add(user)

                await session.commit()
                await session.refresh(user)

            return user

    async def save_user_token(
        self,
        user_id: int,
        token_data: str
    ) -> None:
        async with self.session_factory() as session:
            stmt = delete(UserToken).where(UserToken.user_id == user_id)
            await session.execute(stmt)

            user_token = UserToken(
                user_id=user_id,
                token_data=token_data
            )
            session.add(user_token)
            await session.commit()

    async def get_user_token(
        self,
        user_id: int
    ) -> str | None:
        async with self.session_factory() as session:
            stmt = select(UserToken).where(UserToken.user_id == user_id)
            result = await session.execute(stmt)
            user_token = result.scalar_one_or_none()

            return user_token.token_data if user_token else None

    async def increment_skips(
        self,
        user_id: int,
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
            stmt = select(Subject).where(
                and_(
                    Subject.name == subject_name,
                    Subject.user_id == user_id
                )
            )
            result = await session.execute(stmt)
            subject = result.scalar_one_or_none()

            if subject:
                subject.skips += count

                await session.commit()
                await session.refresh(subject)

                return subject

            else:
                raise SubjectNotFound(f"Не найден предмет {subject_name}")
            

    async def decrement_skips(
        self,
        user_id: int,
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
        if count <= 0:
            raise InvalidCount(f"Невозможно уменьшить пропуски на {count}")

        async with self.session_factory() as session:
            stmt = select(Subject).where(
                and_(
                    Subject.name == subject_name,
                    Subject.user_id == user_id
                )
            )
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
            user_id: int,
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
            stmt = select(Subject).where(
                and_(
                    Subject.name == subject_name,
                    Subject.user_id == user_id
                )
            )
            result = await session.execute(stmt)
            subject = result.scalar_one_or_none()

            if subject:
                raise SubjectAlreadyExists(
                    f"Предмет {subject_name} уже есть в базе данных"
                )

            new_subject = Subject(
                user_id=user_id,
                name=subject_name,
                skips=skips,
                criticality=criticality
            )

            session.add(new_subject)
            await session.commit()
            await session.refresh(new_subject)

            return new_subject

    async def get_all(self, user_id: int) -> list[Subject]:
        """Возвращает все предметы из БД

        Args:
            user_id: идентификатор пользователя в базе данных.

        Returns:
            список всех предметов в базе данных.
        """

        async with self.session_factory() as session:
            stmt = select(Subject).where(Subject.user_id == user_id)

            result = await session.execute(stmt)
            
            subjects = result.scalars().all()

            if not subjects:
                raise SubjectAlreadyExists("Не было найдено предметов")

            return list(subjects)
