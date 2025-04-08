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
make install
```

3. Activate the virtual environment:

```bash
make shell
```

5. Run tests:

```bash
make test-all
```

## 🧪 Environment Setup

```bash
cp ./environments/.env.local.example ./environments/.env.local
cp ./environments/.env.local.example ./environments/.env.docker
```

Edit `.env.local` and `.env.docker` and set your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

🛠 Note: Make sure that the value of DATABASE_HOST is:
• localhost in .env.local (when running the app locally)
• db in .env.docker (when running via Docker Compose)

## 🚀 Running the Project with Docker Compose

1. Build the Docker images:

```bash
make docker-build
```

2. Start the services:

```bash
make docker-up
```

3. Run database migrations:

```bash
make docker-migrate
```

Note: You can use `make docker-init` to run all the above commands in sequence.

4. Load documents for vector database:

```bash
make docker-load-documents DIR=./docs
```

5. To stop and remove all containers:

```bash
make docker-down
```

The API will be available at http://localhost:8000/

## 🎨 User Interface

The project includes a Streamlit-based user interface with the following features:

- Text chat with RAG support
- Audio message processing (supports WAV and MP3)
- Conversation management
- Language selection

To use it:

1. Install UI dependencies:

```bash
make install-ui
```

2. Run the Streamlit interface:

```bash
make run-ui
```

Access the UI at http://localhost:8501

## 🏗️ System Architecture

The application follows Hexagonal Architecture with these layers:

### Domain Layer

- **Entities**: Core business objects ([`ConversationEntity`](chatapp/domain/entities/conversation.py), [`MessageEntity`](chatapp/domain/entities/message.py), [`UserEntity`](chatapp/domain/entities/user.py))
- **Repositories**: Abstract interfaces for data persistence
- **Exceptions**: Custom domain exceptions for better error handling

### Application Layer

- **Use Cases**: Business logic implementation
  - [`CreateConversationUseCase`](chatapp/application/create_conversation_use_case.py): Handles conversation creation
  - [`ProcessMessageUseCase`](chatapp/application/process_message_use_case.py): Manages message processing
  - [`ProcessMessageAudioUseCase`](chatapp/application/process_message_audio_use_case.py): Manages audio message processing
  - [`CreateConversationSummaryUseCase`](chatapp/application/create_conversation_summary_use_case.py): Generates summaries and extracts data

### Infrastructure Layer

- **Repositories**: Concrete implementations of repository interfaces
- **Services**: External service integrations (e.g., LLM service)
- **Database**: Data persistence implementations

### 🧱 System Architecture

<img width="1235" alt="Captura de pantalla 2025-03-25 a las 22 30 48" src="https://github.com/user-attachments/assets/cec9cd76-6b36-4ca7-84f7-2593d960bd03" />

## [`ProcessMessageUseCase`](chatapp/application/process_message_use_case.py)

<img width="1063" alt="Captura de pantalla 2025-03-25 a las 22 53 08" src="https://github.com/user-attachments/assets/e05ddc27-ee5c-4140-b077-96df5d57df22" />

### Key Design Decisions

1. **Hexagonal Architecture**

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

- Authentication & Authorization: Secures your API and lets you control who can access and do what — essential for scaling and multi-user environments.
- Real-time updates: Delivers a modern, responsive UX by pushing updates instantly — ideal for live messaging and better user engagement.
- Add API documentation (e.g., OpenAPI/Swagger): Makes your API easy to understand and integrate, reducing confusion and speeding up collaboration.
- Prompting: Well-structured prompts improve response quality, control tone, and adapt behavior — critical when using LLMs.
- Add message pagination: Boosts performance and scalability by handling long conversations more efficiently.
- Add monitoring and logging: Provides visibility into system health, helping you catch issues early and optimize behavior based on real usage.
- Add integration tests: Ensure the full system works as expected — not just in pieces, but end-to-end, which builds confidence and stability.

## [sample conversation](./sample_conversation.txt)
