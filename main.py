import asyncio

from src.tools import api_resource
from langchain.prompts import PromptTemplate
from langchain_google_community import CalendarSearchEvents, GetCalendarsInfo
from src.chat_agent import agent_executor
from src.tools import tools_descriptions
from src.prompts import react_prompt_str

# query = input("Вопрос >>> ")
query = "Привет! Какие у меня мероприятия будут дальше на сегодняшний день?"
print(query)
async def main():
    stream = agent_executor.astream_events({
        "input": query,
        "tools": "\n".join(tools_descriptions)
    },)

    async for event in stream:
        if event["event"] == "on_chat_model_stream":
            print(event["data"]["chunk"].content, flush=True, end="")

if __name__ == "__main__":
    asyncio.run(main())
