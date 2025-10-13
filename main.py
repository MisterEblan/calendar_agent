from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import (
    get_google_credentials,
    build_calendar_service
)

credentials = get_google_credentials(
    token_file="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file="credentials.json",
)

api_resource = build_calendar_service(credentials)
toolkit = CalendarToolkit(api_resource=api_resource)

tools = toolkit.get_tools()

info = tools[3].invoke({})
result = tools[1].invoke(input={
    "calendars_info": info,
    "min_datetime": "2025-10-13 00:00:00",
    "max_datetime": "2025-10-15 00:00:00"
})

print(result)
