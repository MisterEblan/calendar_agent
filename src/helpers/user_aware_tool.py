from collections.abc import Callable
from functools import wraps

from langchain_core.tools import tool

def user_aware_tool(user_id: int) -> Callable:

    def decorator(func: Callable):
        @wraps
        async def wrapper(*args, **kwargs):
            return await func(user_id, *args, **kwargs)

        return tool(wrapper)
    return decorator
