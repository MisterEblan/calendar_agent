"""Исключения при работе с базой данных"""

class DatabaseException(Exception):
    """Базовое исключение для ошибок базы данных"""
    pass

class SubjectNotFound(DatabaseException):
    """Не найден предмет"""
    pass

class InvalidCount(DatabaseException):
    """Указан count <= 0"""
    pass

class SubjectAlreadyExists(DatabaseException):
    """В базе уже существует данный предмет"""
    pass
