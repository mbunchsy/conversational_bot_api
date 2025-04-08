from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist

from chatapp.domain.entities.message import MessageEntity
from chatapp.domain.repositories.message_repository import MessageRepository
from chatapp.infrastructure.models.message_db import MessageDB

class MessageDBRepository(MessageRepository):
    def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        try:
            message_db = MessageDB.objects.get(id=message_id)
            return message_db.to_entity()
        except ObjectDoesNotExist:
            return None

    def save(self, message: MessageEntity, conversation_id: str) -> MessageEntity:
        message_db = MessageDB.from_entity(message, conversation_id)
        message_db.save()
        return message_db.to_entity()

    def delete(self, message_id: str) -> None:
        MessageDB.objects.filter(id=message_id).delete()

    def get_by_conversation_id(self, conversation_id: str) -> List[MessageEntity]:
        messages = MessageDB.objects.filter(conversation_id=conversation_id).order_by('created_at')
        return [msg.to_entity() for msg in messages]