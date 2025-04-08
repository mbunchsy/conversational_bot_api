import os
import logging
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError, APITimeoutError, InternalServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import tempfile
from chatapp.domain.exceptions.llm.generic_error import LLMGenericError
from chatapp.domain.entities.conversation import ConversationEntity
from chatapp.domain.entities.message import MessageEntity
from chatapp.infrastructure.models.llm_data_response import LLMDataServiceResponse
from chatapp.infrastructure.models.llm_data_response_mapper import LLMDataResponseMapper
from chatapp.domain.services.llm_service import LLMService
from chatapp.domain.exceptions.llm.authentication_error import LLMAuthenticationError
from chatapp.domain.exceptions.llm.rate_limit_error import LLMRateLimitError
from chatapp.domain.exceptions.llm.connection_error import LLMConnectionError
from chatapp.domain.exceptions.validation_error import ValidationError

TEMPERATURE = 0.7

logger = logging.getLogger(__name__)

class LLMDataService(LLMService):
    def __init__(self):
        apiKey = os.getenv("OPENAI_API_KEY")
        if not apiKey:
            raise LLMAuthenticationError(
                message="OPENAI_API_KEY not configured in environment variables",
                details={"env_var": "OPENAI_API_KEY"}
            )
        self.client = OpenAI(api_key=apiKey)
        logger.info("LLMDataService initialized successfully")

    @retry(
        retry=retry_if_exception_type((APIConnectionError, RateLimitError, APITimeoutError, InternalServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_response(self, conversation: ConversationEntity) -> MessageEntity:
        try:
            openaiResponse = self.client.chat.completions.create(
                model=conversation.model,
                messages=conversation.get_memory(),
                temperature=TEMPERATURE,
                response_format={"type": "text"}
            )

            response = LLMDataResponseMapper.to_domain(LLMDataServiceResponse(openaiResponse))
            logger.info(f"Response generated successfully: {response.content[:50]}...")
            return response

        except AuthenticationError as e:
            logger.error(f"Error authenticating with OpenAI: {str(e)}")
            raise LLMAuthenticationError(details={"original_error": str(e)})

        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise LLMRateLimitError(details={"original_error": str(e)})

        except APIConnectionError as e:
            logger.error(f"Connection error with OpenAI: {str(e)}")
            raise LLMConnectionError(details={"original_error": str(e)})

        except APIError as e:
            logger.error(f"Error in the OpenAI API: {str(e)}")
            raise LLMConnectionError(
                message=f"Error in the OpenAI API: {str(e)}",
                details={"original_error": str(e)}
            )

        except Exception as e:
            logger.exception("Unexpected error processing the message")
            raise LLMGenericError(
                message="Unexpected error processing the message",
                details={"original_error": str(e)}
            )

    def generate_transcription(self, audio_file: bytes) -> str:
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_file:
                temp_file.write(audio_file)
                temp_file.flush()
                
                with open(temp_file.name, 'rb') as audio:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        response_format="text"
                    )
                    
                    return response

        except AuthenticationError as e:
            logger.error(f"Error authenticating with OpenAI: {str(e)}")
            raise LLMAuthenticationError(
                message="Invalid API key",
                details={"original_error": str(e)}
            )

        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise LLMRateLimitError(
                message="Too many requests",
                details={"original_error": str(e)}
            )

        except APIConnectionError as e:
            logger.error(f"Connection error with OpenAI: {str(e)}")
            raise LLMConnectionError(
                message="Could not connect to OpenAI",
                details={"original_error": str(e)}
            )

        except APIError as e:
            logger.error(f"Error in the OpenAI API: {str(e)}")
            if "invalid file format" in str(e).lower():
                raise ValidationError(
                    message="Invalid audio format",
                    details={"original_error": str(e)}
                )
            raise LLMConnectionError(
                message="OpenAI API error",
                details={"original_error": str(e)}
            )

        except Exception as e:
            logger.exception("Unexpected error processing audio")
            raise LLMGenericError(
                message="Unexpected error during transcription",
                details={"original_error": str(e)}
            )