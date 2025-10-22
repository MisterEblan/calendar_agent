from langchain.agents import AgentExecutor

from ..ai.tools.utils import create_calendar_tools, create_user_tools
from ..ai.agents import init_tool_calling_agent

import asyncio

class AgentManager:

    def __init__(self):
        self.user_agents: dict[int, AgentExecutor] = {}
        self.lock = asyncio.Lock()

    async def create_agent_for_user(self, user_id: int) -> AgentExecutor:
        async with self.lock:
            if user_id not in self.user_agents:
                await self._create_new_agent(user_id)
            return self.user_agents[user_id]

    async def _create_new_agent(self, user_id: int) -> None:
        db_tools = create_user_tools(user_id)
        calendar_tools = await create_calendar_tools(user_id)

        tools = db_tools + calendar_tools

        agent = init_tool_calling_agent(tools)

        self.user_agents[user_id] = agent


