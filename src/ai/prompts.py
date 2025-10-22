"""Модуль с промптами для моделей"""

from ..config import prompts

prompt_str = prompts["default"]
# react_prompt_str = prompts["react"]


# react_prompt = ChatPromptTemplate.from_messages([
#     ("system", react_prompt_str),
# ])
# react_prompt.input_variables = ["messages", "remaining_steps"]
# react_prompt.partial_variables = {
#     "tools": tools_descriptions,
#     "tool_names": tools_names
# }
