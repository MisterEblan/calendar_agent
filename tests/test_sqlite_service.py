import pytest
from src.db import (
    SqliteService,
    SubjectCriticality,
    InvalidCount,
    SubjectAlreadyExists,
    SubjectNotFound
)

class TestAddSubject:
    """Тесты для добавления предметов"""
    
    @pytest.mark.asyncio
    async def test_add_subject_success(self, sqlite_service: SqliteService):
        """Успешное добавление предмета"""
        subject = await sqlite_service.add_subject(
            "Математика",
            skips=5,
            criticality=SubjectCriticality.HIGH
        )
        
        assert subject.name == "Математика"
        assert subject.skips == 5
        assert subject.criticality == SubjectCriticality.HIGH
        assert subject.id is not None
    
    @pytest.mark.asyncio
    async def test_add_subject_default_criticality(self, sqlite_service: SqliteService):
        """Добавление предмета с критичностью по умолчанию"""
        subject = await sqlite_service.add_subject("Физика", skips=2)
        
        assert subject.criticality == SubjectCriticality.MEDIUM
    
    @pytest.mark.asyncio
    async def test_add_subject_invalid_skips_zero(self, sqlite_service: SqliteService):
        """Ошибка при попытке добавить предмет с 0 пропусками"""
        with pytest.raises(InvalidCount, match="положительным числом"):
            await sqlite_service.add_subject("Химия", skips=0)
    
    @pytest.mark.asyncio
    async def test_add_subject_invalid_skips_negative(self, sqlite_service: SqliteService):
        """Ошибка при попытке добавить предмет с отрицательными пропусками"""
        with pytest.raises(InvalidCount, match="положительным числом"):
            await sqlite_service.add_subject("Биология", skips=-5)
    
    @pytest.mark.asyncio
    async def test_add_subject_already_exists(self, sqlite_service: SqliteService):
        """Ошибка при добавлении существующего предмета"""
        await sqlite_service.add_subject("Математика", skips=3)
        
        with pytest.raises(SubjectAlreadyExists, match="уже есть в базе"):
            await sqlite_service.add_subject("Математика", skips=5)

class TestIncrementSkips:
    """Тесты для увеличения пропусков"""
    
    @pytest.mark.asyncio
    async def test_increment_skips_success(self, service_with_data: SqliteService):
        """Успешное увеличение пропусков"""
        subject = await service_with_data.increment_skips("Математика", 2)
        
        assert subject.name == "Математика"
        assert subject.skips == 5  # Было 3, добавили 2
    
    @pytest.mark.asyncio
    async def test_increment_skips_by_one(self, service_with_data: SqliteService):
        """Увеличение пропусков на 1"""
        subject = await service_with_data.increment_skips("Физика", 1)
        
        assert subject.skips == 2  # Было 1, добавили 1
    
    @pytest.mark.asyncio
    async def test_increment_skips_large_number(self, service_with_data: SqliteService):
        """Увеличение пропусков на большое число"""
        subject = await service_with_data.increment_skips("История", 100)
        
        assert subject.skips == 105  # Было 5, добавили 100
    
    @pytest.mark.asyncio
    async def test_increment_skips_invalid_count_zero(
        self,
        service_with_data: SqliteService
    ):
        """Ошибка при попытке увеличить на 0"""
        with pytest.raises(InvalidCount, match="Невозможно увеличить"):
            await service_with_data.increment_skips("Математика", 0)
    
    @pytest.mark.asyncio
    async def test_increment_skips_invalid_count_negative(
        self,
        service_with_data: SqliteService
    ):
        """Ошибка при попытке увеличить на отрицательное число"""
        with pytest.raises(InvalidCount, match="Невозможно увеличить"):
            await service_with_data.increment_skips("Математика", -5)
    
    @pytest.mark.asyncio
    async def test_increment_skips_subject_not_found(
        self,
        service_with_data: SqliteService
    ):
        """Ошибка при попытке увеличить пропуски несуществующего предмета"""
        with pytest.raises(SubjectNotFound, match="Не найден предмет"):
            await service_with_data.increment_skips("Астрономия", 1)


class TestDecrementSkips:
    """Тесты для уменьшения пропусков"""
    
    @pytest.mark.asyncio
    async def test_decrement_skips_success(self, service_with_data: SqliteService):
        """Успешное уменьшение пропусков"""
        subject = await service_with_data.decrement_skips("История", 2)
        
        assert subject.name == "История"
        assert subject.skips == 3  # Было 5, убавили 2
    
    @pytest.mark.asyncio
    async def test_decrement_skips_default_one(
        self,
        service_with_data: SqliteService
    ):
        """Уменьшение пропусков на 1 по умолчанию"""
        subject = await service_with_data.decrement_skips("Математика")
        
        assert subject.skips == 2  # Было 3, убавили 1
    
    @pytest.mark.asyncio
    async def test_decrement_skips_prevents_negative(
        self,
        service_with_data: SqliteService
    ):
        """Уменьшение не может привести к отрицательным значениям"""
        with pytest.raises(InvalidCount, match="Невозможно уменьшить пропуски"):
            await service_with_data.decrement_skips("Физика", 5)  # Было 1
    
    @pytest.mark.asyncio
    async def test_decrement_skips_invalid_count_zero(
        self,
        service_with_data: SqliteService
    ):
        """Ошибка при попытке уменьшить на 0"""
        with pytest.raises(InvalidCount, match="Невозможно уменьшить"):
            await service_with_data.decrement_skips("Математика", 0)
    
    @pytest.mark.asyncio
    async def test_decrement_skips_invalid_count_negative(
        self,
        service_with_data: SqliteService
    ):
        """Ошибка при попытке уменьшить на отрицательное число"""
        with pytest.raises(InvalidCount, match="Невозможно уменьшить"):
            await service_with_data.decrement_skips("Математика", -3)
    
    @pytest.mark.asyncio
    async def test_decrement_skips_subject_not_found(
        self,
        service_with_data: SqliteService
    ):
        """Ошибка при попытке уменьшить пропуски несуществующего предмета"""
        with pytest.raises(SubjectNotFound, match="Не найден предмет"):
            await service_with_data.decrement_skips("География", 1)


class TestGetAll:
    """Тесты для получения всех предметов"""
    
    @pytest.mark.asyncio
    async def test_get_all_success(self, service_with_data: SqliteService):
        """Успешное получение всех предметов"""
        subjects = await service_with_data.get_all()
        
        assert len(subjects) == 3
        assert isinstance(subjects, list)
        
        names = {s.name for s in subjects}
        assert names == {"Математика", "Физика", "История"}
    
    @pytest.mark.asyncio
    async def test_get_all_empty_database(self, sqlite_service: SqliteService):
        """Пустая база возвращает пустой список"""
        subjects = await sqlite_service.get_all()
        assert subjects == []
        assert isinstance(subjects, list)
    
    @pytest.mark.asyncio
    async def test_get_all_returns_list_type(
        self,
        service_with_data: SqliteService
    ):
        """Проверка, что возвращается именно list"""
        subjects = await service_with_data.get_all()
        
        assert type(subjects) is list
    
    @pytest.mark.asyncio
    async def test_get_all_subjects_have_all_fields(
        self,
        service_with_data: SqliteService
    ):
        """Проверка, что все поля предметов заполнены"""
        subjects = await service_with_data.get_all()
        
        for subject in subjects:
            assert subject.id is not None
            assert subject.name is not None
            assert subject.skips >= 0
            assert subject.criticality in SubjectCriticality
