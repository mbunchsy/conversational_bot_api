from chatapp.domain.entities.conversation import ConversationStatus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chatapp.infrastructure.presenters.conversation_presenter import ConversationPresenter
from chatapp.container import Container
from chatapp.domain.exceptions.validation_error import ValidationError

class CreateConversationSummaryView(APIView):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = Container()
        self.use_case = container.create_conversation_summary_use_case()

    def post(self, request, conversation_id: str) -> Response:
        conversation_status = request.data.get('conversation_status')

        if not conversation_status or not isinstance(conversation_status, str):
            raise ValidationError({
                "conversation_status": "This field is required and must be a string."
            })

        self.use_case.execute(conversation_id, ConversationStatus(conversation_status))

        return Response(status=status.HTTP_204_NO_CONTENT)
        