# System Patterns

## System Architecture
The application follows a microservice-like architecture with a FastAPI backend, a Celery worker for asynchronous tasks, and Supabase as the backend-as-a-service providing database, storage, and authentication.

```mermaid
graph LR
    User[User] --> Frontend[Frontend UI (Vue.js)]
    Frontend --> Backend[FastAPI Backend]
    Backend --> Supabase[Supabase]
    Backend --> Redis[Redis (Queue)]
    Redis --> CeleryWorker[Celery Worker]
    CeleryWorker --> Supabase
    Backend --> OpenRouter[OpenRouter API]

    Supabase --> PostgreSQL[PostgreSQL Database]
    Supabase --> Storage[Supabase Storage]
    Supabase --> Auth[Supabase Auth]
    Supabase --> EdgeFunctions[Supabase Edge Functions (RPC)]

    CeleryWorker --> Storage
    CeleryWorker --> PostgreSQL
    CeleryWorker --> EdgeFunctions
    Backend --> PostgreSQL
    Backend --> Auth
```

## Key Technical Decisions
- **FastAPI:** Chosen for its performance and ease of use for building APIs.
- **SQLModel:** Provides a convenient way to define database models and interact with the PostgreSQL database.
- **Supabase:** Selected as a comprehensive backend-as-a-service, simplifying database, authentication, and storage management.
- **Celery/Redis:** Used for handling asynchronous tasks like document processing to avoid blocking the main API thread.
- **pgvector:** Enables efficient vector storage and similarity search within the PostgreSQL database.
- **Supabase RPC for Embeddings:** Centralizes the embedding generation logic and securely handles the API key within Supabase Vault.
- **OpenRouter for Report Generation:** Provides flexibility in choosing LLMs for generating report content.
- **OpenAI Python SDK:** Utilized to interact with OpenRouter due to its compatibility and ease of integration.

## Design Patterns in Use
- **API Gateway Pattern:** FastAPI acts as the entry point for frontend requests, routing them to appropriate handlers.
- **Worker Pattern:** Celery worker processes time-consuming tasks asynchronously.
- **Repository Pattern (Implicit):** SQLModel interactions abstract some database access logic.
- **Dependency Injection:** FastAPI's dependency injection is used for managing database sessions and user authentication.
- **Retrieval Augmented Generation (RAG):** The core pattern for report generation, combining vector search for relevant context with an LLM.

## Component Relationships
- **Frontend <-> Backend:** Communicates via REST API calls.
- **Backend <-> Supabase:** Interacts with database, storage, and authentication services.
- **Backend <-> Redis:** Pushes document processing tasks to the queue.
- **Backend <-> OpenRouter:** Makes API calls for report content generation.
- **Celery Worker <-> Redis:** Consumes tasks from the queue.
- **Celery Worker <-> Supabase:** Downloads documents from storage, saves parsed content and chunks to the database, and calls the embedding RPC.
- **Backend (Search Router) <-> PostgreSQL:** Executes raw SQL queries for vector search.
- **Supabase RPC `generate_embedding` <-> OpenAI API:** The RPC function makes an external HTTP request to the OpenAI Embeddings API.

## Critical Implementation Paths
- **Document Processing:** Upload -> Backend Endpoint -> Celery Task -> Download from Storage -> Parse -> Chunk -> Generate Embeddings (via Supabase RPC) -> Save Chunks to DB.
- **Report Generation:** User Prompt -> Backend Endpoint -> Generate Prompt Embedding (via Supabase RPC) -> Vector Search (raw SQL) -> Retrieve Relevant Chunks -> Prepare Context -> Call OpenRouter API -> Generate Report Content -> Save Report to DB.
- **User Authentication:** Registration/Login -> Backend Endpoint -> Supabase Auth -> Generate/Verify Tokens.
