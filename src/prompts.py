from langchain.prompts import ChatPromptTemplate, PromptTemplate
from .config.config import prompts
from .tools import tools_descriptions
from .tools import tools

prompt_str = prompts["default"]
react_prompt_str = prompts["react"]

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_str),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])
react_prompt_str_eng = """You are smart agent that helps to make schedule.
You have tools that you should use if needed.

My Calendar ID: boy4rov.da@gmail.com.
It needed to get_current_datetime as argument.

Tools:

{tools}

Use provided format:

Question: input question.
Thought: you need to think about what to do next.
Action: one of the tools from [{tool_names}].
Action Input: input arguments or nothing.
Observation: result of action.
... (Thought/Action/Action Input/Observation can be repeated)
Thought: Now i know the final answer.
Final Answer: final answer on question.

Question: {input}
Thought:{agent_scratchpad}"""

react_prompt = PromptTemplate(
    template=react_prompt_str,
    input_variables=["input", "agent_scratchpad"],
    partial_variables={
        "tools": "\n".join(tools_descriptions),
        "tool_names": ", ".join(t.name for t in tools)
    }
)

"""
Пример.
Question: какие у меня есть мероприятия на этой неделе?
Thought: Какие есть календари?
Action: get_calendars_info
Action Input: None
Observation: <Результат>
Thought: Теперь у меня есть данные о календарях. Мне нужно получить сегодняшнюю дату, чтобы понять, за какое время запрашивать мероприятия.
Action: get_current_datetime
Action Input: None
Observation: <Результат>
Thought: Теперь у меня есть сегодняшняя дата. Я могу запросить мероприятия пользователя.
Action: calendar_search_events
Action Input: 
Observation: <Результат>
Final Answer: у Вас следующие мероприятия...
"""
