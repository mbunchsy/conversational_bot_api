from rest_framework import serializers

from chatapp.domain.models.create_conversation_input import CreateConversationInput

class CreateConversationInputDTO(serializers.Serializer):
    user_id = serializers.CharField(
        required=False,
        allow_null=True,
        default=None,
        error_messages={
            'invalid': 'Invalid user ID format'
        }
    )
    language = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Language is required'
        }
    )

    def to_domain(self) -> CreateConversationInput:
        return CreateConversationInput(
            user_id=self.validated_data["user_id"],
            language=self.validated_data["language"]
        )