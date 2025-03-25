from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from chatapp.container import Container
from chatapp.application.process_message_audio_use_case import ProcessMessageAudioCommand
from chatapp.infrastructure.presenters.conversation_presenter import ConversationPresenter
from chatapp.domain.exceptions.validation_error import ValidationError

class ConversationAudioView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = Container()
        self._process_message_audio_use_case = container.process_message_audio_use_case()

    def post(self, request, conversation_id: str):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            raise ValidationError(
                {"error": "No audio file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        content_type = audio_file.content_type
        if not content_type.startswith('audio/'):
            raise ValidationError(
                {"error": "Invalid file type. Must be an audio file"},
                status=status.HTTP_400_BAD_REQUEST
            )

        audio_content = audio_file.read()
            
        command = ProcessMessageAudioCommand(
            audio_content=audio_content,
            language=request.data.get('language')
        )
            
        conversation = self._process_message_audio_use_case.execute(conversation_id, command)
            
        return Response(ConversationPresenter(conversation).data, status=status.HTTP_200_OK)
