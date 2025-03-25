from dataclasses import dataclass
from openai.types.chat import ChatCompletion

@dataclass
class LLMDataServiceResponse:
    completion: ChatCompletion
