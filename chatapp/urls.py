from django.urls import path

from chatapp.infrastructure.controllers.conversation_view import ConversationView
from chatapp.infrastructure.controllers.create_conversation_view import CreateConversationView
from chatapp.infrastructure.controllers.create_conversation_summary_view import CreateConversationSummaryView
from chatapp.infrastructure.controllers.conversation_audio_view import ConversationAudioView


urlpatterns = [
    path("v1/conversations/<str:conversation_id>/summary", CreateConversationSummaryView.as_view(), name="create_conversation_summary"),
    path("v1/conversations/<str:conversation_id>/message", ConversationView.as_view(), name="conversation"),
    path("v1/conversations/<str:conversation_id>/message_audio", ConversationAudioView.as_view(), name="conversation_audio"),
    path("v1/conversations/start", CreateConversationView.as_view(), name="create_conversation"),
]
