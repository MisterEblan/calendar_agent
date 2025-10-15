import json
from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import (
    get_google_credentials,
    build_calendar_service
)

weekday_mapping = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

# def get_today() -> str:
#     """Возвращает сегодняшнюю дату в виде строки
#
#     Returns:
#         str: строка вида `%Y-%m-%d %H:%M:%S`"""
#     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


credentials = get_google_credentials(
    token_file="token.json",
    scopes=[
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    client_secrets_file="credentials.json",
)

api_resource = build_calendar_service(credentials)
toolkit = CalendarToolkit(api_resource=api_resource)

tools = toolkit.get_tools()

for t in tools:
    name = t.name
    description = t.description
    args = t.args

tools_descriptions = [
    f"{t.name}: {t.description}" for t in tools
]
