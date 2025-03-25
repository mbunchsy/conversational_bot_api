from abc import ABC, abstractmethod

from chatapp.domain.entities.conversation import ConversationEntity
from chatapp.domain.entities.message import MessageEntity

class LLMService(ABC):
    @abstractmethod
    def generate_response(self, conversation: ConversationEntity) -> MessageEntity:
        pass

    @abstractmethod
    def generate_transcription(self, audio_file: bytes) -> str:
        pass
    