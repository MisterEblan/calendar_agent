"""Создание контекста для промпта"""

from ..db.models import Subject


class ContextBuilder:

    @staticmethod
    def from_subjects(subjects: list[Subject]) -> str:
        subjects_strings: list[str] = []
        for subject in subjects:
            s = f"{subject.name} ({subject.criticality}): {subject.skips}"

            subjects_strings.append(s)

        return "\n".join(subjects_strings)
