import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from chatapp.application.create_conversation_summary_use_case import (
    CreateConversationSummaryUseCase,
    SYSTEM_PROMPT_SUMMARY,
    SYSTEM_PROMPT_DATE_EXTRACTION
)
from chatapp.domain.entities.conversation import ConversationEntity, ConversationStatus
from chatapp.domain.entities.message import MessageEntity, MessageRole
from chatapp.domain.entities.user import UserEntity
from chatapp.domain.exceptions.internal_error import InternalError
from chatapp.domain.exceptions.not_found_error import NotFoundError

class TestCreateConversationSummaryUseCase(unittest.TestCase):
    def setUp(self):
        self.conversation_repository = Mock()
        self.llm_service = Mock()
        self.use_case = CreateConversationSummaryUseCase(
            conversation_repository=self.conversation_repository,
            llm_service=self.llm_service
        )
        
        # Common test data
        self.user = UserEntity(_id=str(uuid4()), name="Test User")
        self.conversation_id = str(uuid4())
        self.conversation = ConversationEntity(user=self.user, _id=self.conversation_id)

    def test_create_summary_successfully(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.conversation_repository.update.return_value = self.conversation

        # Create a list to store the prompts used in each call
        prompts_used = []
        def capture_prompt(conversation):
            prompts_used.append(conversation.system_prompt.content)
            return MessageEntity(role=MessageRole.ASSISTANT, content="Test summary" if len(prompts_used) == 1 else "Test extraction")
        
        self.llm_service.generate_response.side_effect = capture_prompt

        # Act
        result = self.use_case.execute(self.conversation_id, ConversationStatus.COMPLETED)

        # Assert
        self.assertEqual(result, self.conversation)
        self.assertEqual(result.summary, "Test summary")
        self.assertEqual(result.extracted_data, "Test extraction")
        self.assertEqual(result.status, ConversationStatus.COMPLETED)

        # Verify system prompts were updated correctly
        self.assertEqual(len(prompts_used), 2)
        self.assertEqual(prompts_used[0], SYSTEM_PROMPT_SUMMARY)
        self.assertEqual(prompts_used[1], SYSTEM_PROMPT_DATE_EXTRACTION)

        self.conversation_repository.update.assert_called_once_with(self.conversation)

    def test_conversation_not_found(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotFoundError) as context:
            self.use_case.execute(self.conversation_id, ConversationStatus.COMPLETED)
        
        self.assertEqual(context.exception.code, "CONVERSATION_NOT_FOUND")
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.llm_service.generate_response.assert_not_called()
        self.conversation_repository.update.assert_not_called()

    def test_llm_service_error_during_summary(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.llm_service.generate_response.side_effect = Exception("LLM Error")

        # Act & Assert
        with self.assertRaises(InternalError) as context:
            self.use_case.execute(self.conversation_id, ConversationStatus.FAILED)
        
        self.assertIn("Failed to end the conversation", str(context.exception))
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.llm_service.generate_response.assert_called_once()
        self.conversation_repository.update.assert_not_called()

    def test_llm_service_error_during_extraction(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = self.conversation
        summary_response = MessageEntity(role=MessageRole.ASSISTANT, content="Test summary")
        self.llm_service.generate_response.side_effect = [
            summary_response,
            Exception("LLM Error")
        ]

        # Act & Assert
        with self.assertRaises(InternalError) as context:
            self.use_case.execute(self.conversation_id, ConversationStatus.FAILED)
        
        self.assertIn("Failed to end the conversation", str(context.exception))
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.assertEqual(self.llm_service.generate_response.call_count, 2)
        self.conversation_repository.update.assert_not_called()

    def test_repository_update_error(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = self.conversation
        summary_response = MessageEntity(role=MessageRole.ASSISTANT, content="Test summary")
        extraction_response = MessageEntity(role=MessageRole.ASSISTANT, content="Test extraction")
        self.llm_service.generate_response.side_effect = [summary_response, extraction_response]
        self.conversation_repository.update.side_effect = Exception("DB Error")

        # Act & Assert
        with self.assertRaises(InternalError) as context:
            self.use_case.execute(self.conversation_id, ConversationStatus.COMPLETED)
        
        self.assertIn("Failed to end the conversation", str(context.exception))
        self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
        self.assertEqual(self.llm_service.generate_response.call_count, 2)
        self.conversation_repository.update.assert_called_once()

    def test_status_update(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.conversation_repository.update.return_value = self.conversation

        status_responses = []
        for status in [
            ConversationStatus.COMPLETED,
            ConversationStatus.FAILED,
            ConversationStatus.PENDING_REVIEW,
            ConversationStatus.ARCHIVED,
            ConversationStatus.DELETED
        ]:
            status_responses.extend([
                MessageEntity(role=MessageRole.ASSISTANT, content=f"Summary for {status.value}"),
                MessageEntity(role=MessageRole.ASSISTANT, content=f"Extraction for {status.value}")
            ])
        self.llm_service.generate_response.side_effect = status_responses

        # Test each possible status
        for status in [
            ConversationStatus.COMPLETED,
            ConversationStatus.FAILED,
            ConversationStatus.PENDING_REVIEW,
            ConversationStatus.ARCHIVED,
            ConversationStatus.DELETED
        ]:
            with self.subTest(status=status):
                # Reset mocks for each subtest
                self.conversation_repository.get_by_id.reset_mock()
                self.conversation_repository.update.reset_mock()
                self.conversation = ConversationEntity(user=self.user, _id=self.conversation_id)
                self.conversation_repository.get_by_id.return_value = self.conversation
                self.conversation_repository.update.return_value = self.conversation

                # Act
                result = self.use_case.execute(self.conversation_id, status)

                # Assert
                self.assertEqual(result.status, status)
                self.assertEqual(result.summary, f"Summary for {status.value}")
                self.assertEqual(result.extracted_data, f"Extraction for {status.value}")
                self.conversation_repository.get_by_id.assert_called_once_with(self.conversation_id)
                self.conversation_repository.update.assert_called_once_with(self.conversation)

    def test_only_one_system_prompt_in_memory(self):
        # Arrange
        self.conversation_repository.get_by_id.return_value = self.conversation
        self.conversation_repository.update.return_value = self.conversation

        # Create a list to store conversations passed to update
        saved_conversations = []
        def capture_conversation(conversation):
            saved_conversations.append(conversation)
            return conversation
        self.conversation_repository.update.side_effect = capture_conversation

        # Mock LLM responses with valid data
        def generate_response(conversation):
            if conversation.system_prompt.content == SYSTEM_PROMPT_SUMMARY:
                return MessageEntity(role=MessageRole.ASSISTANT, content="Test summary")
            else:
                return MessageEntity(role=MessageRole.ASSISTANT, content='{"key": "value"}')
        self.llm_service.generate_response.side_effect = generate_response

        # Act
        self.use_case.execute(self.conversation_id, ConversationStatus.COMPLETED)

        # Assert
        # Verify the final conversation state that was saved
        final_conversation = saved_conversations[-1]
        self.assertEqual(final_conversation.system_prompt.content, SYSTEM_PROMPT_DATE_EXTRACTION)

    def test_update_system_prompt_replaces_previous(self):
        # Arrange
        first_prompt = MessageEntity(role=MessageRole.SYSTEM, content="First prompt")
        second_prompt = MessageEntity(role=MessageRole.SYSTEM, content="Second prompt")
        
        # Act
        self.conversation.update_system_prompt(first_prompt)
        self.conversation.update_system_prompt(second_prompt)
        
        # Assert
        self.assertEqual(self.conversation.system_prompt.content, "Second prompt")