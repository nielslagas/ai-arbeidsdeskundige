from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from backend.models import Case, Document, Chunk, GeneratedReport, ReportTemplate
from backend.dependencies import get_session, get_current_user, supabase # Import dependencies from backend.dependencies
from uuid import UUID
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY must be set in the environment variables")

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

# Choose a model (using openrouter/auto for automatic selection)
GENERATION_MODEL = "openrouter/auto"

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/generate/{case_id}")
async def generate_report(
    case_id: UUID,
    prompt: str, # User's prompt for the report
    template_id: Optional[UUID] = None, # Optional template to use
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    Generates a report for a specific case based on a prompt and relevant document chunks.
    """
    print(f"Received generate report request for case_id: {case_id}, prompt: {prompt}")
    # 1. Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == user.id)).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found or not owned by user")

    # 2. (Optional) Retrieve Report Template
    template = None
    if template_id:
        template = session.exec(select(ReportTemplate).where(ReportTemplate.id == template_id)).first()
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report template not found")
        # TODO: Add logic to ensure user can use this template (e.g., public or owned by user)

    # 3. Generate embedding for the user prompt
    # This will use the same Supabase embedding method as in the Celery worker and search router
    # The Supabase RPC 'generate_embedding' is assumed to use an appropriate embedding model (e.g., OpenAI's text-embedding-ada-002)
    try:
        print("Attempting to generate embedding for prompt...")
        # Call Supabase embeddings API using the 'generate_embedding' RPC
        # Ensure this RPC is set up in your Supabase project and uses the desired embedding model.
        # The input parameter name ('content') and output structure ('embedding') must match the RPC definition.
        response = supabase.rpc('generate_embedding', {'content': prompt}).execute()

        print(f"Supabase embedding RPC raw response: {response}")

        if response.data and response.data[0] and response.data[0].get('embedding'):
            prompt_embedding = response.data[0]['embedding']
            print(f"Generated embedding for prompt: '{prompt}'. Extracted embedding data: {prompt_embedding}")
        else:
            # Handle cases where embedding generation fails or returns no embedding
            print(f"Supabase embedding generation failed or returned no embedding for prompt: '{prompt}'. Response: {response}")
            raise Exception("Failed to generate prompt embedding.")

    except Exception as e:
        print(f"Error during Supabase embedding generation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate prompt embedding: {e}")

    # 4. Perform vector similarity search to find relevant chunks
    # This requires the 'pgvector' extension enabled in your Supabase database
    # and the 'embedding' column in the 'chunk' table to be of type 'vector'.
    # The '<->' operator is used for the cosine similarity search in pgvector (lower is better).
    # You might need to adjust the query based on your specific pgvector setup and desired similarity metric/threshold.

    try:
        print("Attempting vector similarity search...")
        # Ensure the prompt_embedding is a list of floats
        if not isinstance(prompt_embedding, list) or not all(isinstance(i, (int, float)) for i in prompt_embedding):
             raise ValueError("Prompt embedding is not a valid list of floats.")

        # Convert UUIDs to strings for the raw SQL query parameters
        case_id_str = str(case_id)
        prompt_embedding_str = str(prompt_embedding) # pgvector expects array literal format e.g., '[1.0, 2.0, ...]'

        # Construct the raw SQL query
        # Using parameterized query to prevent SQL injection
        sql_query = """
        SELECT
            chunk.id,
            chunk.content,
            chunk.document_id,
            chunk.embedding <-> :prompt_embedding AS similarity
        FROM chunk
        JOIN document ON chunk.document_id = document.id
        WHERE document.case_id = :case_id
        ORDER BY similarity
        LIMIT 10; -- Get top 10 most similar chunks for RAG context
        """

        # Execute the raw SQL query
        from sqlalchemy import text
        results = session.exec(
            text(sql_query),
            {"prompt_embedding": prompt_embedding_str, "case_id": case_id_str}
        ).all()

        # Extract content from relevant chunks
        relevant_chunks_content = [row[1] for row in results]
        print(f"Found {len(relevant_chunks_content)} relevant chunks for case {case_id}.")
        print("Vector similarity search completed.")

    except Exception as e:
        # Log the error and raise an HTTPException
        print(f"Error during vector search for case {case_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Vector search failed: {e}")


    # 5. Prepare context for the LLM
    context = "\n\n".join(relevant_chunks_content) # Join chunks with double newline
    print(f"Prepared context for LLM from {len(relevant_chunks_content)} chunks.")

    # 6. Generate report content using an LLM (RAG)
    # Integrate with OpenRouter API using OpenAI SDK
    try:
        print("Attempting LLM report generation via OpenRouter...")
        # Construct the messages for the LLM, including the context and user prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates report sections based on provided context."},
            {"role": "user", "content": f"""
            Based on the following document excerpts (context) and the user's request (prompt), generate a draft report section.

            Context:
            {context}

            User Request:
            {prompt}

            Generated Report Section:
            """}
        ]

        # Generate content using the LLM via OpenRouter
        response = client.chat.completions.create(
            model=GENERATION_MODEL,
            messages=messages,
            # Add optional headers for OpenRouter if needed for tracking/ranking
            # extra_headers={
            #     "HTTP-Referer": "YOUR_SITE_URL", # Replace with your site URL
            #     "X-Title": "AD-Rapport Generator AI", # Replace with your site name
            # },
        )

        # Extract generated text from the response
        generated_text = response.choices[0].message.content
        print(f"Generated report content using {GENERATION_MODEL} via OpenRouter.")

        # Structure the generated content (this might need refinement based on template)
        generated_content = {
            "prompt": prompt,
            "generated_text": generated_text,
            "used_chunks_count": len(relevant_chunks_content),
            # You might want to include chunk IDs or other metadata here
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM report generation failed: {e}")

    # 7. Save the generated report to the database
    print("Attempting to save generated report to database...")
    new_report = GeneratedReport(
        case_id=case_id,
        template_id=template_id, # Can be None if no template is used
        content=generated_content,
        generation_status="completed" # Assuming generation is synchronous for now
    )

    session.add(new_report)
    session.commit()
    session.refresh(new_report)
    print(f"Saved generated report {new_report.id} for case {case_id}.")

    return {"report_id": new_report.id, "content": new_report.content}

# TODO: Add endpoints for listing, retrieving, updating, and deleting reports
# Similar to the cases and documents routers.
