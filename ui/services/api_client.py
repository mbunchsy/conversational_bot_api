import requests
from typing import Dict, Any, Optional
import mimetypes

from ui.models import ConversationStatus
from ..config import UIConfig

class APIClient:
    def __init__(self, base_url: str = None):
        config = UIConfig()
        self.base_url = (base_url or config.API_URL).rstrip('/')
        if not self.base_url.endswith('/api/v1'):
            self.base_url += '/api/v1'
        self.config = config

    def create_conversation(self, user_id: str, language: str = None) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(
                f"{self.base_url}/conversations/start",
                json={
                    "language": language or self.config.LANGUAGE
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating conversation: {str(e)}")
            return None

    def send_message(self, conversation_id: str, message: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(
                f"{self.base_url}/conversations/{conversation_id}/message",
                json={
                    "content": message,
                    "language": self.config.LANGUAGE
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error sending message: {str(e)}")
            return None

    def _get_content_type(self, filename: str) -> str:
        if filename.lower().endswith('.mp3'):
            return 'audio/mpeg'
        elif filename.lower().endswith('.wav'):
            return 'audio/wav'
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def send_audio(self, conversation_id: str, audio_file, language: str = None) -> Optional[Dict[str, Any]]:
        try:
            content_type = self._get_content_type(audio_file.name)
            files = {
                'audio': (
                    audio_file.name,
                    audio_file,
                    content_type
                )
            }
            data = {'language': language or self.config.LANGUAGE}
            
            response = requests.post(
                f"{self.base_url}/conversations/{conversation_id}/message_audio",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error sending audio: {str(e)}")
            return None

    def get_summary(self, conversation_id: str, status: ConversationStatus) -> None:
        try:
            response = requests.post(
                f"{self.base_url}/conversations/{conversation_id}/summary",
                json={
                    "conversation_status": status.value,
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting summary: {str(e)}")
            return None