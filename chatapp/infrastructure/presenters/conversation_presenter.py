from rest_framework import serializers

from chatapp.infrastructure.presenters.message_presenter import MessagePresenter

class ConversationPresenter(serializers.Serializer):
    id = serializers.CharField()
    messages = MessagePresenter(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'messages': MessagePresenter(instance.messages, many=True).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }