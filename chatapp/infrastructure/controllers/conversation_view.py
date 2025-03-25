from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from chatapp.infrastructure.dtos.send_message_dto import SendMessageInputDTO
from chatapp.infrastructure.presenters.conversation_presenter import ConversationPresenter
from chatapp.container import Container

class ConversationView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = Container()
        self.use_case = container.process_message_use_case()

    def post(self, request, conversation_id: str):
        serializer = SendMessageInputDTO(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        conversation = self.use_case.execute(
            serializer.to_domain(conversation_id)
        )

        return Response(ConversationPresenter(conversation).data, status=status.HTTP_200_OK)