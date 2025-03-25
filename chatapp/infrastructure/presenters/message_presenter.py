from rest_framework import serializers

class MessagePresenter(serializers.Serializer):
    id = serializers.CharField()
    content = serializers.CharField()
    role = serializers.CharField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'content': instance.content,
            'role': instance.role.value,
            'created_at': instance.created_at
        }