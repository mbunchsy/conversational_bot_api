from cmd import PROMPT
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID, uuid4
import json
import tiktoken

from chatapp.domain.exceptions.validation_error import ValidationError
from chatapp.domain.entities.user import UserEntity
from chatapp.domain.entities.message import MessageEntity, MessageRole
from chatapp.domain.models.llm_message_model import LLMMessage

PROMPT_LANGUAGE = """
    Conversation Language:

The assistant's response language must follow these rules:

1. If the user explicitly requests to be answered in a specific language, or if the user's preferred language can be clearly inferred from the conversation context, the assistant must respond in that language.

2. If the user has already sent a message and no specific language was requested, the assistant must reply in the same language as the user's message.

3. If the user has not sent any message yet and no preferred language can be inferred, the assistant must use the conversation's preconfigured language: **{language}**.

   - If the configured language is 'es', respond in **Spanish**.
   - If the configured language is 'en', respond in **English**.
   - If the configured language is 'fr', respond in **French**.

The goal is to keep the conversation smooth, coherent, and personalized for the user, without switching languages arbitrarily. Do not translate previous messages — always respond directly in the appropriate language..
"""

RAG_CONTEXT = """
If additional context has been provided at the end of this prompt, it is relevant to the current situation. This context has been retrieved from external documents (knowledge base, policies, FAQs, etc.) to help answer the question more effectively.

Use it only if it's relevant to the user's query.

---

<< BEGIN RAG CONTEXT >>
{{rag_context}}
<< END RAG CONTEXT >>
"""

ENCODING_MODEL = "cl100k_base"

class ConversationStatus(Enum):
    ACTIVE = "active"            
    COMPLETED = "completed"     
    PENDING_REVIEW = "pending_review"
    FAILED = "failed"
    ARCHIVED = "archived"
    DELETED = "deleted"

@dataclass
class ConversationEntity:
    user: UserEntity
    _id: str = field(default_factory=lambda: str(uuid4()))
    messages: List[MessageEntity] = field(default_factory=list)
    _new_messages: List[MessageEntity] = field(default_factory=list, init=False)
    extracted_data: Optional[dict] = None
    summary: Optional[str] = None
    status: ConversationStatus = ConversationStatus.ACTIVE
    language: str = "es"
    model: Optional[str] = "gpt-4o"
    context_windows: int = 128000
    max_out_tokens: int = 16384
    system_prompt: Optional[MessageEntity] = None
    rag_context: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        pass
    
    @property
    def id(self) -> str:
        return self._id
            
    def add_message(self, message: MessageEntity) -> MessageEntity:
        self.messages.append(message)
        self._new_messages.append(message)
        self.updated_at = datetime.now()

        return message
    
    def get_unsaved_messages(self) -> List[MessageEntity]:
        return self._new_messages.copy()
    
    def mark_messages_as_saved(self) -> None:
        self._new_messages.clear()
    
    def _count_tokens(self, text: str) -> int:
        if not text:
            return 0
        
        encoding = tiktoken.get_encoding(ENCODING_MODEL)
        return len(encoding.encode(text))

    def _get_messages_within_token_limit(self) -> List[LLMMessage]:
        messages = []
        
        if self.system_prompt:
            if self.language:
                self.system_prompt.content += f"\n\n{PROMPT_LANGUAGE.format(language=self.language)}"
            if self.rag_context:
                self.system_prompt.content += f"\n\n{RAG_CONTEXT.format(rag_context=self.rag_context)}"

            messages.append(self.system_prompt.to_llm_format())
            token_count = self._count_tokens(self.system_prompt.content)
        else:
            token_count = 0
        
        available_tokens = self.context_windows - self.max_out_tokens
        
        recent_messages = []
        for msg in reversed(self.messages):
            if msg.role == MessageRole.SYSTEM:
                continue
            
            msg_tokens = self._count_tokens(msg.content)
            
            if token_count + msg_tokens > available_tokens:
                break
                
            token_count += msg_tokens
            recent_messages.insert(0, msg.to_llm_format())
        
        messages.extend(recent_messages)
        return messages

    def get_memory(self) -> List[LLMMessage]:
        return self._get_messages_within_token_limit()
    
    def clear(self) -> None:
        self.messages.clear()
        self._new_messages.clear()
        self.updated_at = datetime.now()
    
    def update_extracted_data(self, data: dict[str, Any]) -> None:
        self._validate_extracted_data(data)
        self.extracted_data = data
        self.updated_at = datetime.now()
    
    def update_summary(self, new_summary: str) -> None:
        if not new_summary or not new_summary.strip():
            raise ValidationError(
                message="The summary cannot be empty",
                code="INVALID_SUMMARY",
                details={
                    "field": "summary",
                    "value": new_summary,
                    "expected": "Non-empty string"
                }
            )
        
        self.summary = new_summary.strip()
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: ConversationStatus) -> None:        
        if self.status == new_status:
            return
        
        self.status = new_status
        self.updated_at = datetime.now()

    def _load_system_prompt(self) -> None:
        for message in self.messages:
            if message.role == MessageRole.SYSTEM:
                self.system_prompt = message
                break
            
    def get_system_prompt(self) -> Optional[MessageEntity]:
        return self.system_prompt

    def update_system_prompt(self, new_system_prompt: MessageEntity) -> None:
        if not new_system_prompt or not new_system_prompt.content.strip():
            raise ValidationError(
                message="System prompt cannot be empty",
                code="INVALID_SYSTEM_PROMPT",
                details={"received": new_system_prompt}
            )
        
        if new_system_prompt.role != MessageRole.SYSTEM:
            raise ValidationError(
                message="System prompt must have role 'system'",
                code="INVALID_SYSTEM_PROMPT_ROLE",
                details={"received_role": new_system_prompt.role}
            )
        
        self.system_prompt = new_system_prompt
        self.updated_at = datetime.now()

    def update_language(self, new_language: str) -> None:
        if self.language.lower() == new_language.lower():
            return

        if not new_language.isalpha() or len(new_language) != 2:
            raise ValidationError(
                message="Language must be a two-letter ISO code",
                code="INVALID_LANGUAGE_FORMAT",
                details={"field": "language", "value": new_language}
            )
            
        self.language = new_language.lower()
        self.updated_at = datetime.now()

    def update_rag_context(self, context: Optional[str]) -> None:
        self.rag_context = context
        self.updated_at = datetime.now()

    @staticmethod
    def _validate_extracted_data(data: dict[str, Any]) -> None:
        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            raise ValidationError(
                message="Extracted data must be serializable to JSON",
                code="INVALID_EXTRACTED_DATA",
                details={
                    "field": "extracted_data",
                    "error": str(e)
                }
            )
