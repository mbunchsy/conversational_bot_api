from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import logging

from chatapp.container import Container
from chatapp.application.process_message_audio_use_case import ProcessMessageAudioCommand
from chatapp.infrastructure.presenters.conversation_presenter import ConversationPresenter
from chatapp.domain.exceptions.validation_error import ValidationError

logger = logging.getLogger(__name__)

class ConversationAudioView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    ALLOWED_EXTENSIONS = ('.wav', '.mp3')
    ALLOWED_CONTENT_TYPES = {
        'audio/wav', 'audio/x-wav',
        'audio/mpeg', 'audio/mp3'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        container = Container()
        self._process_message_audio_use_case = container.process_message_audio_use_case()

    def post(self, request, conversation_id: str):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            raise ValidationError(
                message="No audio file provided"
            )

        filename = audio_file.name.lower()
        content_type = audio_file.content_type.lower()
        
        logger.info(f"Received file: {filename} with content type: {content_type}")
        
        if not any(filename.endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise ValidationError(
                message="Invalid file type. Must be a WAV or MP3 file"
            )

        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                message=f"Invalid content type. Must be WAV or MP3. Received: {content_type}"
            )

        audio_content = audio_file.read()
            
        command = ProcessMessageAudioCommand(
            audio_content=audio_content,
            language=request.data.get('language')
        )
            
        conversation = self._process_message_audio_use_case.execute(conversation_id, command)
            
        return Response(ConversationPresenter(conversation).data, status=status.HTTP_200_OK)
