import unittest
from unittest.mock import Mock
from uuid import uuid4

from chatapp.application.process_message_use_case import ProcessMessageUseCase
from chatapp.domain.entities.conversation import ConversationEntity
from chatapp.domain.entities.message import MessageEntity, MessageRole
from chatapp.domain.entities.user import UserEntity
from chatapp.domain.exceptions.internal_error import InternalError
from chatapp.domain.exceptions.not_found_error import NotFoundError
from chatapp.domain.models.create_message_input import CreateMessageInput

class TestProcessMessageUseCase(unittest.TestCase):
    def setUp(self):
        self.llm_service = Mock()
        self.conversation_repository = Mock()
        self.rag_service = Mock()
        self.use_case = ProcessMessageUseCase(
            llm_service=self.llm_service,
            conversation_repository=self.conversation_repository,
            rag_service=self.rag_service
        )
        
        self.user = UserEntity(_id=str(uuid4()), name="Test User")
        self.conversation_id = str(uuid4())
        self.conversation = ConversationEntity(user=self.user, _id=self.conversation_id)

    def test_process_message_successfully(self):
        user_message = MessageEntity(role=MessageRole.USER, content="Hello")
        message_input = CreateMessageInput(
            conversation_id=self.conversation_id,
            new_message=user_message,
            language="es"
        )
        
        llm_response = MessageEntity(role=MessageRole.ASSISTANT, content="Hi there!")
        self.llm_service.generate_response.return_value = llm_response
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.conversation_repository.update.return_value = self.conversation

        result = self.use_case.execute(message_input)

        self.assertEqual(result, self.conversation)
        self.assertEqual(len(result.messages), 2)
        self.assertEqual(result.messages[-2], user_message)
        self.assertEqual(result.messages[-1], llm_response)
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.llm_service.generate_response.assert_called_once_with(self.conversation)
        self.conversation_repository.update.assert_called_once_with(self.conversation)

    def test_conversation_not_found(self):
        self.conversation_repository.get_by_id.return_value = None
        message_input = CreateMessageInput(
            conversation_id=self.conversation_id,
            new_message=MessageEntity(role=MessageRole.USER, content="Hello"),
            language="es"
        )

        with self.assertRaises(NotFoundError) as context:
            self.use_case.execute(message_input)
        
        self.assertEqual(context.exception.code, "CONVERSATION_NOT_FOUND")
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.llm_service.generate_response.assert_not_called()
        self.conversation_repository.update.assert_not_called()

    def test_llm_service_error(self):
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.llm_service.generate_response.side_effect = Exception("LLM Error")
        message_input = CreateMessageInput(
            conversation_id=self.conversation_id,
            new_message=MessageEntity(role=MessageRole.USER, content="Hello"),
            language="es"
        )

        with self.assertRaises(InternalError) as context:
            self.use_case.execute(message_input)
        
        self.assertIn("Error processing the prompt", str(context.exception))
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.llm_service.generate_response.assert_called_once_with(self.conversation)
        self.conversation_repository.update.assert_not_called()

    def test_message_order_preserved(self):
        existing_message = MessageEntity(role=MessageRole.USER, content="Previous message")
        self.conversation.add_message(existing_message)
        
        new_message = MessageEntity(role=MessageRole.USER, content="New message")
        message_input = CreateMessageInput(
            conversation_id=self.conversation_id,
            new_message=new_message,
            language="es"
        )
        
        llm_response = MessageEntity(role=MessageRole.ASSISTANT, content="Response")
        self.llm_service.generate_response.return_value = llm_response
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.conversation_repository.update.return_value = self.conversation

        result = self.use_case.execute(message_input)

        self.assertEqual(len(result.messages), 3)
        self.assertEqual(result.messages[0], existing_message)
        self.assertEqual(result.messages[1], new_message)
        self.assertEqual(result.messages[2], llm_response)

    def test_conversation_updated_correctly(self):
        original_conversation = ConversationEntity(user=self.user, _id=self.conversation_id)
        updated_conversation = ConversationEntity(user=self.user, _id=self.conversation_id)
        
        message = MessageEntity(role=MessageRole.USER, content="Hello")
        message_input = CreateMessageInput(
            conversation_id=self.conversation_id,
            new_message=message,
            language="es"
        )
        
        llm_response = MessageEntity(role=MessageRole.ASSISTANT, content="Hi!")
        
        self.conversation_repository.get_by_id.return_value = original_conversation
        self.llm_service.generate_response.return_value = llm_response
        self.conversation_repository.update.return_value = updated_conversation

        result = self.use_case.execute(message_input)

        self.assertEqual(result, updated_conversation)
        self.conversation_repository.update.assert_called_once()
        conversation_to_update = self.conversation_repository.update.call_args[0][0]
        self.assertEqual(len(conversation_to_update.messages), 2)
        self.assertEqual(conversation_to_update.messages[0], message)
        self.assertEqual(conversation_to_update.messages[1], llm_response)
        