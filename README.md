# 🤖 Bot Conversational API — Technical Assignment

## 📌 Overview

This project is a conversational API system developed using Django and PostgreSQL, designed as a technical assignment for a AI engineer role. It supports:
• Multi-turn conversations
• System prompts
• Audio and text input
• Multilingual support
• RAG (Retrieval-Augmented Generation) using pgvector over PostgreSQL

## ⚙️ Setup Instructions

### 🛠 Prerequisites

- Python 3.10 or higher
- Make (for running commands)
- Poetry (for dependency management)

### Installation

1. Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:

```bash
poetry install
```

3. Activate the virtual environment:

```bash
poetry shell
```

4. Run tests:

```bash
make test-all
```

## 🧪 Environment

```bash
cp ./environments/.env.local.example ./environments/.env.local
```

## 🚀 Run the project

```bash
make docker-init
```

This will:
• Build containers
• Start services
• Run Django migrations
• Expose API at http://localhost:8000/

## System Architecture Overview

The application follows a Clean Architecture pattern with these main layers:

### Domain Layer

- **Entities**: Core business objects (`ConversationEntity`, `MessageEntity`, `UserEntity`)
- **Repositories**: Abstract interfaces for data persistence
- **Exceptions**: Custom domain exceptions for better error handling

### Application Layer

- **Use Cases**: Business logic implementation
  - `CreateConversationUseCase`: Handles conversation creation
  - `ProcessMessageUseCase`: Manages message processing
  - `ProcessMessageAudioUseCase`: Manages audio message processing
  - `CreateConversationSummaryUseCase`: Generates summaries and extracts data

### Infrastructure Layer

- **Repositories**: Concrete implementations of repository interfaces
- **Services**: External service integrations (e.g., LLM service)
- **Database**: Data persistence implementations

### 🧱 System Architecture

.| User Input | --> | Django REST API | --> | Use Case Layer |
.+----------------+ +---------------------+ +-----------------------+
.                                                 | | |
.                                                 | | |
.                                    +------+------+ +------+------+
.                                    | MessageRepo | | LLMService |
.                                    | UserRepo | | RAGService |
.                                    +-------------+ +--------------+

[PGVector DB] <---> Document Ingestor + Similarity Search

### Key Design Decisions

1. **Clean Architecture**

   - Clear separation of concerns
   - Domain-driven design principles
   - Independence from external frameworks
   - Easily testable components

2. **Use Case Pattern**

   - Each business operation is encapsulated in a use case
   - Single responsibility principle
   - Easy to extend and modify

3. **Domain Model**

   - Rich domain model with business logic
   - Encapsulated validation
   - Immutable where possible
   - Clear state transitions

4. **Error Handling**

   - Custom domain exceptions
   - Proper error propagation
   - Detailed error messages and codes
   - Validation at domain level

5. **Testing Strategy**
   - Comprehensive unit tests
   - Mock external dependencies
   - Test different scenarios and edge cases
   - Clear test organization

## Potential Improvements

1. **Technical Improvements**

   - Add integration tests
   - Implement caching layer
   - Add API documentation (e.g., OpenAPI/Swagger)
   - Add monitoring and logging
   - Implement rate limiting
   - Add authentication and authorization

2. **Feature Enhancements**

   - Support for multiple LLM providers
   - Conversation analytics
   - Bulk operations support
   - Real-time updates
   - Message attachments support

3. **Performance Optimizations**

   - Implement conversation archiving
   - Add message pagination
   - Optimize token counting
   - Add database indexes
   - Implement caching strategies

4. **Developer Experience**

   - Add development environment setup script
   - Improve error messages
   - Add more code examples
   - Create contribution guidelines
   - Add CI/CD pipeline

5. **Documentation**
   - Add API documentation
   - Include architecture diagrams
   - Add code examples
   - Document best practices
   - Create troubleshooting guide
