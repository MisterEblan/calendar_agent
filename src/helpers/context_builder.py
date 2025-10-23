"""Создание контекста для промпта"""

from ..db.models import Subject


class ContextBuilder:
    """Класс для создания контекста"""

    @staticmethod
    def from_subjects(subjects: list[Subject]) -> str:
        """Создаёт контекст из полученных в базе предметов

        Args:
            subjects: предметы из базы данных.

        Returns:
            Строки формата
            `[Название] ([Критичность]): [количество пропусков]`
        """
        subjects_strings: list[str] = []
        for subject in subjects:
            s = f"{subject.name} ({subject.criticality}): {subject.skips}"

            subjects_strings.append(s)

        return "\n".join(subjects_strings)
