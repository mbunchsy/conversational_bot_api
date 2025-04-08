from rest_framework import serializers
from datetime import datetime

from chatapp.domain.models.create_message_input import CreateMessageInput
from chatapp.domain.entities.message import MessageEntity, MessageRole

class SendMessageInputDTO(serializers.Serializer):
    content = serializers.CharField(
        min_length=2,
        max_length=200000,
        error_messages={
            'required': 'Message content is required',
            'blank': 'Message content cannot be blank',
            'min_length': 'Message must be at least 1 character long',
            'max_length': 'Message cannot exceed 200000 characters'
        }
    )

    language = serializers.CharField(
        required=True,
        error_messages={
            'required': 'El lenguaje es requerido'
        }
    )

    def validate_content(self, value):
        if value.strip() == '':
            raise serializers.ValidationError('Content cannot be empty or contain only whitespace')
        return value.strip()

    def to_domain(self, conversation_id: str) -> CreateMessageInput:
        return CreateMessageInput(
            conversation_id,
            language=self.validated_data["language"],
            new_message=MessageEntity(
                content=self.validated_data["content"],
                role=MessageRole.USER
            )
        )
