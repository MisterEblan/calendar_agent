"""Модуль с агентами"""

from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core._api import LangChainDeprecationWarning
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama

from ..config import models_params, prompts
import warnings

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

params = models_params["ollama"]

llm = ChatOllama(
    **params,
)

# === TOOL CALLING ===

def init_tool_calling_agent(tools: list[BaseTool]) -> AgentExecutor:
    """Создание tool-calling агента с указанными инструментами

    Args:
        tools: инструменты агента

    Returns:
        исполнитель агента.
    """

    tools_descriptions = "\n".join(f"{t.name}: {t.description}" for t in tools)

    default_prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["default"]),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    default_prompt.input_variables = ["input", "agent_scratchpad"]
    default_prompt.partial_variables = {
        "tools": tools_descriptions,
    }
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
