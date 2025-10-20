"""Модуль с инструментами для агентов"""

from langchain_google_community import CalendarToolkit, GetCurrentDatetime
from langchain_google_community.calendar.utils import (
    get_google_credentials,
    build_calendar_service
)

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

tools_descriptions = [
    f"{t.name}: {t.description}" for t in tools
]
tools_names = ", ".join(t.name for t in tools)

get_current_datetime = GetCurrentDatetime(api_resource=api_resource)
