from dataclasses import dataclass

@dataclass
class CreateConversationInput:
    user_id: str
    language: str