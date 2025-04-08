from typing import TypedDict, Literal

class LLMMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str