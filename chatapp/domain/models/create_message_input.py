from dataclasses import dataclass
from chatapp.domain.entities.message import MessageEntity

@dataclass
class CreateMessageInput:
    conversation_id: str
    language: str
    new_message: MessageEntity