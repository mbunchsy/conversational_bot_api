from abc import ABC, abstractmethod
from typing import Optional, List

from chatapp.domain.entities.conversation import ConversationEntity

class ConversationRepository(ABC):    
    @abstractmethod
    def get_by_id(self, conversation_id: str) -> Optional[ConversationEntity]:
        pass

    @abstractmethod
    def create(self, conversation: ConversationEntity) -> ConversationEntity:
        pass

    @abstractmethod
    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        pass
        
    @abstractmethod
    def delete(self, conversation_id: str) -> None:
        pass

    @abstractmethod
    def get_all_by_user_id(self, user_id: str) -> List[ConversationEntity]:
        pass