"""Модуль с промптами для моделей"""

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .config.config import prompts
from .tools import (
        tools_descriptions,
        tools_names,
        get_current_datetime,
)

prompt_str = prompts["default"]
react_prompt_str = prompts["react"]

default_prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_str),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])
default_prompt.input_variables = ["input", "agent_scratchpad"]
default_prompt.partial_variables = {
    "tools": tools_descriptions,
    "current_datetime": get_current_datetime._run(),
}

react_prompt = ChatPromptTemplate.from_messages([
    ("system", react_prompt_str),
])
react_prompt.input_variables = ["messages", "remaining_steps"]
react_prompt.partial_variables = {
    "tools": tools_descriptions,
    "tool_names": tools_names
}
