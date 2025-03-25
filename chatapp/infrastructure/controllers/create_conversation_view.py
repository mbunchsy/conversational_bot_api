from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chatapp.infrastructure.presenters.conversation_presenter import ConversationPresenter
from chatapp.infrastructure.dtos.create_conversation_dto import CreateConversationInputDTO
from chatapp.container import Container

class CreateConversationView(APIView):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = Container()
        self.use_case = container.create_conversation_use_case()

    def post(self, request) -> Response:
        serializer = CreateConversationInputDTO(data=request.data)
        if not serializer.is_valid():
            return Response(input_dto.errors, status=status.HTTP_400_BAD_REQUEST)
            
        conversation = self.use_case.execute(
            serializer.to_domain()
        )

        return Response(ConversationPresenter(conversation).data, status=status.HTTP_201_CREATED)
