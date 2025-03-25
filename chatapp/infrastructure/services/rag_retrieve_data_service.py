import os
import logging
from typing import List
from openai import OpenAI
from pgvector.django import L2Distance
from chatapp.infrastructure.models.document_db import DocumentDB

logger = logging.getLogger(__name__)

class RAGRetrieverService:
    def __init__(self):
        apiKey = os.getenv("OPENAI_API_KEY")
        if not apiKey:
            raise LLMAuthenticationError(
                message="OPENAI_API_KEY not configured in environment variables",
                details={"env_var": "OPENAI_API_KEY"}
            )
        self.client = OpenAI(api_key=apiKey)
        logger.info("RAGRetrieverService initialized successfully")

    def get_embedding(self, text: str) -> List[float]:
        try:
            logger.info("🔍 Getting embedding for query")
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
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

    def retrieve_context(self, query: str, k: int = 3) -> str:
        try:
            embedding = self.get_embedding(query)

            docs = DocumentDB.objects.annotate(
                distance=L2Distance("embedding", embedding)
            ).order_by("distance")[:k]

            logger.info(f"Retrieved {len(docs)} documents")
            return "\n\n".join([doc.content for doc in docs])
        except Exception as e:
            logger.error(f"Failed retrieving context: {e}")
            return ""