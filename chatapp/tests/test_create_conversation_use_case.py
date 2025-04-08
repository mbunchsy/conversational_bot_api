import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from chatapp.application.create_conversation_use_case import CreateConversationUseCase
from chatapp.domain.entities.conversation import ConversationEntity
from chatapp.domain.entities.message import MessageEntity, MessageRole
from chatapp.domain.entities.user import UserEntity
from chatapp.domain.exceptions.internal_error import InternalError
from chatapp.domain.exceptions.not_found_error import NotFoundError
from chatapp.domain.models.create_conversation_input import CreateConversationInput

class TestCreateConversationUseCase(unittest.TestCase):
    def setUp(self):
        self.conversation_repository = Mock()
        self.user_repository = Mock()
        self.llm_service = Mock()
        self.use_case = CreateConversationUseCase(
            self.conversation_repository,
            self.user_repository,
            self.llm_service
        )

    def test_create_conversation_with_existing_user(self):
        # Arrange
        user_id = str(uuid4())
        user = UserEntity(_id=user_id, name="Test User")
        self.user_repository.get_by_id.return_value = user
        
        conversation_input = CreateConversationInput(user_id=user_id, language="es")
        expected_conversation = ConversationEntity(user=user, language="es")
        self.conversation_repository.create.return_value = expected_conversation
        
        # Mock LLM response
        assistant_message = MessageEntity(role=MessageRole.ASSISTANT, content="Hello!")
        self.llm_service.generate_response.return_value = assistant_message

        # Act
        result = self.use_case.execute(conversation_input)

        # Assert
        self.assertEqual(result, expected_conversation)
        self.user_repository.get_by_id.assert_called_once_with(user_id)
        self.conversation_repository.create.assert_called_once()
        self.llm_service.generate_response.assert_called_once()

    def test_create_conversation_with_anonymous_user(self):
        # Arrange
        anonymous_user = UserEntity(_id=str(uuid4()), name="Anonymous")
        self.user_repository.create_anonymous.return_value = anonymous_user
        
        conversation_input = CreateConversationInput(user_id=None, language="es")
        expected_conversation = ConversationEntity(user=anonymous_user, language="es")
        self.conversation_repository.create.return_value = expected_conversation
        
        # Mock LLM response
        assistant_message = MessageEntity(role=MessageRole.ASSISTANT, content="Hello!")
        self.llm_service.generate_response.return_value = assistant_message

        # Act
        result = self.use_case.execute(conversation_input)

        # Assert
        self.assertEqual(result, expected_conversation)
        self.user_repository.create_anonymous.assert_called_once()
        self.conversation_repository.create.assert_called_once()
        self.llm_service.generate_response.assert_called_once()

    def test_create_conversation_with_nonexistent_user(self):
        # Arrange
        user_id = str(uuid4())
        self.user_repository.get_by_id.return_value = None
        conversation_input = CreateConversationInput(user_id=user_id, language="es")

        # Act & Assert
        with self.assertRaises(NotFoundError) as context:
            self.use_case.execute(conversation_input)
        
        self.assertEqual(context.exception.code, "USER_NOT_FOUND")
        self.user_repository.get_by_id.assert_called_once_with(user_id)

    def test_create_conversation_handles_llm_error(self):
        # Arrange
        user = UserEntity(_id=str(uuid4()), name="Test User")
        self.user_repository.create_anonymous.return_value = user
        
        conversation_input = CreateConversationInput(user_id=None, language="es")
        self.llm_service.generate_response.side_effect = Exception("LLM Error")

        # Act & Assert
        with self.assertRaises(InternalError) as context:
            self.use_case.execute(conversation_input)
        
        self.assertIn("Error creating the conversation", str(context.exception))
        self.user_repository.create_anonymous.assert_called_once()
        self.llm_service.generate_response.assert_called_once()