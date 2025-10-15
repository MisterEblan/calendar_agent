from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent, create_tool_calling_agent

from .prompts import react_prompt, prompt

from .tools import tools

# model_name = "llama3.2"
model_name = "qwen3:4b"

llm = ChatOllama(
    model=model_name,
    num_thread=16,
    temperature=0.1,
    reasoning=False,
    # num_ctx=64 * 1000
)

agent = create_tool_calling_agent(
    llm=llm, tools=tools, prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
    max_iterations=5,
    verbose=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)
