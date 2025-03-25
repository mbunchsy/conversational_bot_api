import logging
from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_log, after_log

from chatapp.domain.entities.conversation import ConversationEntity
from chatapp.domain.repositories.conversation_repository import ConversationRepository
from chatapp.infrastructure.models.conversation_db import ConversationDB
from chatapp.infrastructure.models.message_db import MessageDB
from chatapp.domain.exceptions.bad_request import BadRequestError
from chatapp.domain.exceptions.validation_error import ValidationError

logger = logging.getLogger(__name__)

class ConversationDBRepository(ConversationRepository):
    def get_by_id(self, conversation_id: str) -> Optional[ConversationEntity]:
        try:
            conversation_db = ConversationDB.objects.select_related('user').prefetch_related('messages').get(id=conversation_id)
            return conversation_db.to_entity()
        except ObjectDoesNotExist:
            return None

    @retry(
        retry=retry_if_exception_type((ValidationError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=4),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO)
    )
    def create(self, conversation: ConversationEntity) -> ConversationEntity:
        if self.get_by_id(conversation.id):
            conversation.generate_new_id()
            raise ValidationError("Duplicate ID, retrying with a new one.")

        conversation_db = ConversationDB.from_entity(conversation)
        conversation_db.save()

        unsaved_messages = conversation.get_unsaved_messages()
        for message in unsaved_messages:
            MessageDB.from_entity(message, conversation_db.id).save()
        conversation.mark_messages_as_saved()

        return self.get_by_id(conversation_db.id)

    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        if not self.get_by_id(conversation.id):
            raise BadRequestError(
                message="The conversation you are trying to update does not exist.",
                code="CONVERSATION_NOT_FOUND",
                details={"conversation_id": conversation.id}
            )

        conversation_db = ConversationDB.objects.get(id=conversation.id)

        conversation_db.extracted_data = conversation.extracted_data
        conversation_db.summary = conversation.summary
        conversation_db.status = conversation.status.value
        conversation_db.save()

        unsaved_messages = conversation.get_unsaved_messages()
        print(unsaved_messages)
        for message in unsaved_messages:
            MessageDB.from_entity(message, conversation_db.id).save()
        conversation.mark_messages_as_saved()

        return self.get_by_id(conversation_db.id)

    def delete(self, conversation_id: str) -> None:
        ConversationDB.objects.filter(id=conversation_id).delete()

    def get_all_by_user_id(self, user_id: str) -> List[ConversationEntity]:
        conversations = ConversationDB.objects.filter(user_id=user_id).select_related('user').prefetch_related('messages')
        return [conv.to_entity() for conv in conversations]
