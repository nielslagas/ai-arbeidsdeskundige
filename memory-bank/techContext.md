# Tech Context

## Technologies Used
- **Backend:** Python (FastAPI, SQLModel, Celery, Redis, python-dotenv, python-docx, openai)
- **Database:** PostgreSQL (Supabase) with pgvector extension
- **Queue:** Redis
- **Object Storage:** Supabase Storage
- **Authentication:** Supabase Auth
- **Embeddings:** OpenAI Embeddings API (called via Supabase RPC `generate_embedding`)
- **LLM for Report Generation:** OpenRouter (accessed via OpenAI Python SDK)
- **Frontend:** Vue.js

## Development Setup
- Local development environment requires Python, Docker (for Redis), and potentially a local Supabase setup or connection to a remote Supabase project.
- Environment variables are managed via a `.env` file.
- Backend dependencies are managed via `requirements.txt`.
- Frontend dependencies are managed via `package.json`.
- Backend runs using `uvicorn`.
- Celery worker runs separately.
- Frontend development server runs using `vite`.

## Technical Constraints
- Reliance on Supabase for database, storage, and authentication.
- Current document parsing is limited to `.docx` and `.txt`.
- Current chunking is basic paragraph-based.
- Embedding generation relies on the configured Supabase RPC.
- Report generation relies on the OpenRouter API.

## Dependencies
- `fastapi`
- `sqlmodel`
- `psycopg2-binary` (for PostgreSQL)
- `supabase` (with `[embeddings]` extra)
- `celery`
- `redis`
- `python-dotenv`
- `python-docx`
- `openai` (for OpenRouter integration)
- `uvicorn`
- `watchfiles`
- Frontend dependencies (managed in `frontend/package.json`): `vue`, `vue-router`, `@supabase/supabase-js`, `pinia` (if used), etc.

## Tool Usage Patterns
- `read_file` and `search_files` for code analysis and understanding.
- `replace_in_file` for targeted code modifications.
- `write_to_file` for creating new files or overwriting existing ones (used for memory bank updates).
- `execute_command` for running backend server, Celery worker, frontend development server, and other CLI tasks.
- `use_mcp_tool` (specifically `context7-mcp`) for fetching documentation.
- `ask_followup_question` for gathering necessary information from the user (e.g., terminal output).
- `attempt_completion` to signal task completion.
- `browser_action` for testing and verifying the frontend UI in a browser.
