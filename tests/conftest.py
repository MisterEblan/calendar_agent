from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.db import AsyncDatabaseService
from src.db.models import SubjectCriticality
from src.db.sqlite_service import SqliteService

@pytest_asyncio.fixture
async def engine() -> AsyncEngine:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False  # Отключаем логирование для тестов
    )
    
    # Предполагается, что Base это DeclarativeBase из models.py
    from src.db.models import Base
    
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Очистка после тестов
    await engine.dispose()

@pytest.fixture
def sqlite_service(engine: AsyncEngine) -> AsyncDatabaseService:
    return SqliteService(engine)

@pytest_asyncio.fixture
async def service_with_data(sqlite_service: SqliteService) -> SqliteService:
    await sqlite_service.add_subject("Математика", skips=3, criticality=SubjectCriticality.HIGH)
    await sqlite_service.add_subject("Физика", skips=1, criticality=SubjectCriticality.MEDIUM)
    await sqlite_service.add_subject("История", skips=5, criticality=SubjectCriticality.LOW)
    return sqlite_service
