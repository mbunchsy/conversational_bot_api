from dataclasses import dataclass
import logging
from typing import Optional

from chatapp.domain.entities.message import MessageEntity, MessageRole
from chatapp.domain.exceptions.not_found_error import NotFoundError
from chatapp.infrastructure.services.llm_data_service import LLMDataService
from chatapp.domain.repositories.conversation_repository import ConversationRepository

@dataclass  
class ProcessMessageAudioCommand:
    audio_content: bytes
    language: Optional[str] = None

logger = logging.getLogger(__name__)

class ProcessMessageAudioUseCase:
    def __init__(self, llm_service: LLMDataService, conversation_repository: ConversationRepository):
        self._llm_service = llm_service
        self._conversation_repository = conversation_repository

    def execute(self, conversation_id: str, command: ProcessMessageAudioCommand) -> str:
        try:
            conversation = self._conversation_repository.get_by_id(conversation_id)
            if not conversation:
                raise NotFoundError(
                    message="Conversation not found",
                    code="CONVERSATION_NOT_FOUND",
                    details={"conversation_id": conversation_id}
                )

            llm_transcription = self._llm_service.generate_transcription(command.audio_content)
            
            conversation.add_message(MessageEntity(role=MessageRole.USER, content=llm_transcription))
            
            llm_response = self._llm_service.generate_response(conversation)
            
            conversation.add_message(llm_response)
            
            return self._conversation_repository.update(conversation)
        except NotFoundError:
            raise
        except Exception as e:
            logger.exception("Error processing the prompt")
            raise InternalError(
                message="Error processing the prompt",
                details={"original_error": str(e)}
            )