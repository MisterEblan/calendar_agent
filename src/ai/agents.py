"""Модуль с агентами"""

from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core._api import LangChainDeprecationWarning
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

from .prompts import react_prompt, default_prompt
from .tools import tools
from ..config import models_params
import warnings

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

params = models_params["ollama"]

llm = ChatOllama(
    **params,
)

# === REACT ===

react_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=react_prompt,
)

# === TOOL CALLING ===

def init_tool_calling_agent(tools: list[BaseTool]) -> AgentExecutor:
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        output_key="output",
        return_messages=True,
        k=5
    )


    tool_calling_agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=default_prompt,
    )
    tool_agent_executor = AgentExecutor(
        name="Помощник по расписанию",
        agent=tool_calling_agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=8,
        memory=memory,
    )
    
    return tool_agent_executor
