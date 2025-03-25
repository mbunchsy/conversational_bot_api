import logging

from chatapp.domain.exceptions.internal_error import InternalError
from chatapp.domain.exceptions.not_found_error import NotFoundError
from chatapp.domain.entities.conversation import ConversationEntity
from chatapp.domain.models.create_message_input import CreateMessageInput
from chatapp.domain.repositories.conversation_repository import ConversationRepository
from chatapp.infrastructure.services.llm_data_service import LLMDataService
from chatapp.domain.services.rag_retrieve_service import RAGRetrieveService

logger = logging.getLogger(__name__)

class ProcessMessageUseCase:

    def __init__(self, llm_service: LLMDataService, conversation_repository: ConversationRepository, rag_service: RAGRetrieveService):
        self._llm_service = llm_service
        self._conversation_repository = conversation_repository
        self._rag_service = rag_service
    
    def execute(self, message_input: CreateMessageInput) -> ConversationEntity:
        try:
            conversation = self._conversation_repository.get_by_id(message_input.conversation_id)
            if not conversation:
                raise NotFoundError(
                    message="Conversation not found",
                    code="CONVERSATION_NOT_FOUND",
                    details={"conversation_id": message_input.conversation_id}
                )

            conversation.add_message(message_input.new_message)

            rag_context = self._rag_service.retrieve_context(message_input.new_message.content)
            if rag_context:
                conversation.update_rag_context(rag_context)

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