import uuid
from django.db import models
from chatapp.domain.entities.message import MessageEntity, MessageRole

class MessageDB(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey('ConversationDB', on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    role = models.CharField(
        max_length=10,
        choices=[(role.value, role.name) for role in MessageRole]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def to_entity(self) -> MessageEntity:
        return MessageEntity(
            _id=str(self.id),
            content=self.content,
            role=MessageRole(self.role)
        )

    @classmethod
    def from_entity(cls, entity: MessageEntity, conversation_id: uuid.UUID) -> 'MessageDB':
        return cls(
            id=uuid.UUID(entity.id) if isinstance(entity.id, str) else entity.id,
            conversation_id=conversation_id,
            content=entity.content,
            role=entity.role.value
        )