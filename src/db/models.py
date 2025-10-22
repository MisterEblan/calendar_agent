"""Модели для работы с базой данных"""

from enum import Enum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class SubjectCriticality(str, Enum):
    """Критичность предмета"""
    LOW = "низкая критичность"
    MEDIUM = "средняя критичность"
    HIGH = "высокая критичность"

class Base(DeclarativeBase):
    pass

class User(Base):
    """Таблица пользователей

    Attributes:
        telegram_id: идентификатор из Telegram.
        username: имя пользователя в Telegram.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(64), unique=True)
    username: Mapped[str]    = mapped_column(String(128))

class UserToken(Base):
    """Таблица токенов пользователей"""
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token_data: Mapped[str] = mapped_column(Text)

class Subject(Base):
    """Таблица с предметами и оценками

    Attributes:
        name: название предмета.
        skips: количество пропусков.
        criticality: критичность предмета.
    """
    __tablename__ = "subjects"

    id: Mapped[int]    = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str]  = mapped_column(String(64))
    skips: Mapped[int] = mapped_column(Integer())
    criticality: Mapped[SubjectCriticality] = mapped_column(
        default=SubjectCriticality
    )
