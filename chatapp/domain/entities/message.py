from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from chatapp.domain.models.llm_message_model import LLMMessage
from chatapp.domain.exceptions.validation_error import ValidationError


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class MessageEntity:
    content: str
    role: MessageRole
    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self._validate_content()
    
    @property
    def id(self) -> str:
        return self._id
    
    def _validate_content(self) -> None:
        if not self.content or not str(self.content).strip():
            raise ValidationError(
                message="The message content cannot be empty.",
                code="INVALID_CONTENT",
                details={
                    "field": "content",
                    "value": self.content,
                    "expected": "Non-empty string"
                }
            )
    
    @property
    def is_user_message(self) -> bool:
        return self.role == MessageRole.USER
    
    @property
    def is_assistant_message(self) -> bool:
        return self.role == MessageRole.ASSISTANT
        
    def to_llm_format(self) -> LLMMessage:
        return {
            "role": self.role.value,
            "content": self.content
        }