from abc import ABC, abstractmethod
from typing import Optional, List

from chatapp.domain.entities.message import MessageEntity

class MessageRepository(ABC):
    @abstractmethod
    def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        pass

    @abstractmethod
    def save(self, message: MessageEntity, conversation_id: str) -> MessageEntity:
        pass

    @abstractmethod
    def delete(self, message_id: str) -> None:
        pass

    @abstractmethod
    def get_by_conversation_id(self, conversation_id: str) -> List[MessageEntity]:
        pass