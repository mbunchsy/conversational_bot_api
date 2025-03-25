from dependency_injector import containers, providers
from dotenv import load_dotenv

from chatapp.application.create_conversation_summary_use_case import CreateConversationSummaryUseCase
from chatapp.infrastructure.services.llm_data_service import LLMDataService
from chatapp.application.process_message_use_case import ProcessMessageUseCase
from chatapp.infrastructure.repository.conversation_db_repository import ConversationDBRepository
from chatapp.infrastructure.repository.user_db_repository import UserDBRepository
from chatapp.infrastructure.repository.message_db_repository import MessageDBRepository
from chatapp.application.create_conversation_use_case import CreateConversationUseCase
from chatapp.application.process_message_audio_use_case import ProcessMessageAudioUseCase
from chatapp.infrastructure.services.rag_retrieve_data_service import RAGRetrieverService


load_dotenv()

class Container(containers.DeclarativeContainer):    
    # Repositories
    conversation_repository = providers.Singleton(
        ConversationDBRepository
    )
    
    user_repository = providers.Singleton(
        UserDBRepository
    )

    message_repository = providers.Singleton(
        MessageDBRepository
    )
    
    # Services
    llm_service = providers.Singleton(LLMDataService)
    
    rag_service = providers.Singleton(
        RAGRetrieverService
    )

    # Use Cases
    process_message_audio_use_case = providers.Factory(
        ProcessMessageAudioUseCase,
        llm_service=llm_service,
        conversation_repository=conversation_repository,
    )

    process_message_use_case = providers.Factory(
        ProcessMessageUseCase,
        llm_service=llm_service,
        conversation_repository=conversation_repository,
        rag_service=rag_service
    )

    create_conversation_use_case = providers.Factory(
        CreateConversationUseCase,
        conversation_repository=conversation_repository,
        user_repository=user_repository,
        llm_service=llm_service,
    )

    create_conversation_summary_use_case = providers.Factory(
        CreateConversationSummaryUseCase,
        conversation_repository=conversation_repository,
        llm_service=llm_service,
    )
