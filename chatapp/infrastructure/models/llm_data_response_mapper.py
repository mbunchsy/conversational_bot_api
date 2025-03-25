from chatapp.domain.entities.message import MessageEntity, MessageRole
from chatapp.infrastructure.models.llm_data_response import LLMDataServiceResponse

class LLMDataResponseMapper:
    @staticmethod
    def to_domain(assistantResponse: LLMDataServiceResponse) -> MessageEntity:
        response = assistantResponse.completion.choices[0].message
        return MessageEntity(
            content=response.content,
            role=MessageRole.ASSISTANT
        )