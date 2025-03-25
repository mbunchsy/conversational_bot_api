import uuid
from typing import List
from django.db import models
from django.db.models import JSONField

from chatapp.domain.entities.conversation import ConversationEntity, ConversationStatus
from .message_db import MessageDB
from .user_db import UserDB

class ConversationDB(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserDB, on_delete=models.CASCADE, related_name='conversations')
    extracted_data = JSONField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.name) for status in ConversationStatus],
        default=ConversationStatus.ACTIVE.value
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'

    def to_entity(self) -> ConversationEntity:
        messages = [msg.to_entity() for msg in self.messages.all()]
        return ConversationEntity(
            _id=str(self.id),
            user=self.user.to_entity(),
            messages=messages,
            extracted_data=self.extracted_data,
            summary=self.summary,
            status=ConversationStatus(self.status)
        )

    @classmethod
    def from_entity(cls, entity: ConversationEntity) -> 'ConversationDB':
        conversation = cls(
            id=uuid.UUID(entity.id) if isinstance(entity.id, str) else entity.id,
            user=UserDB.from_entity(entity.user),
            extracted_data=entity.extracted_data,
            summary=entity.summary,
            status=entity.status.value
        )

        return conversation