"""Движок для работы с базой данных"""

from sqlalchemy.ext.asyncio import create_async_engine
from .models import Base
from ..config import app_config

engine = create_async_engine(app_config.database_url)

async def init_db():
    """Создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
