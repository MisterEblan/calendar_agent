"""Модели для работы с базой данных"""

from enum import Enum
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class SubjectCriticality(str, Enum):
    """Критичность предмета"""
    LOW = "низкая критичность"
    MEDIUM = "средняя критичность"
    HIGH = "высокая критичность"

class Base(DeclarativeBase):
    pass

class Subject(Base):
    """База данных с предметами и оценками

    Attributes:
        name: название предмета.
        skips: количество пропусков.
        criticality: критичность предмета.
    """
    __tablename__ = "subjects"

    id: Mapped[int]    = mapped_column(primary_key=True)
    name: Mapped[str]  = mapped_column(String(64))
    skips: Mapped[int] = mapped_column(Integer())
    criticality: Mapped[SubjectCriticality] = mapped_column(
        default=SubjectCriticality
    )
