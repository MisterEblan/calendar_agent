"""Модуль с инструментами для агентов"""

from google.auth.transport.requests import Request
from langchain_google_community import CalendarToolkit, GetCurrentDatetime
from langchain_google_community.calendar.utils import (
    get_google_credentials,
    build_calendar_service
)

from .db_tools import db_tools

credentials = get_google_credentials(
    token_file="token.json",
    scopes=[
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    client_secrets_file="credentials.json",
)

if credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())

    with open("token.json", "w") as token:
        token.write(credentials.to_json())

api_resource = build_calendar_service(credentials)
toolkit = CalendarToolkit(api_resource=api_resource)

# === Database Tools ===


tools = toolkit.get_tools() + db_tools

tools_descriptions = [
    f"{t.name}: {t.description}" for t in tools
]
tools_names = ", ".join(t.name for t in tools)

get_current_datetime = GetCurrentDatetime(api_resource=api_resource)
