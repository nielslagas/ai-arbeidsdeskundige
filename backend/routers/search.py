from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from backend.models import Case, Document, Chunk
from backend.dependencies import get_session, get_current_user, supabase # Import dependencies from backend.dependencies
from uuid import UUID

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/vector/{case_id}")
async def vector_search(
    case_id: UUID,
    query: str, # User's search query
    limit: int = 10, # Number of results to return
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    Performs a vector similarity search against document chunks within a specific case.
    """
    # 1. Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == user["id"])).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found or not owned by user")

    # 2. Generate embedding for the user query
    # This will use the same Supabase embedding method as in the Celery worker.
    # You might need to configure the embedding model name (e.g., 'text-embedding-ada-002')
    # Refer to Supabase documentation for the exact API call.

    try:
        # Call Supabase embeddings API using the 'generate_embedding' RPC
        # Ensure this RPC is set up in your Supabase project and uses the desired embedding model.
        # The input parameter name ('input_text') and output structure ('embedding') must match the RPC definition.
        response = supabase.rpc('generate_embedding', {'input_text': query}).execute()

        if response.data and response.data[0] and response.data[0].get('embedding'):
            query_embedding = response.data[0]['embedding']
            print(f"Generated embedding for query: '{query}'")
        else:
            # Handle cases where embedding generation fails or returns no embedding
            print(f"Supabase embedding generation failed or returned no embedding for query: '{query}'. Response: {response}")
            raise Exception("Failed to generate query embedding.")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate query embedding: {e}")

    # 3. Perform vector similarity search to find relevant chunks
    # This requires the 'pgvector' extension enabled in your Supabase database
    # and the 'embedding' column in the 'chunk' table to be of type 'vector'.
    # The '<->' operator is used for the cosine similarity search in pgvector (lower is better).
    # You might need to adjust the query based on your specific pgvector setup and desired similarity metric/threshold.

    # Example raw SQL query using pgvector '<->' operator for cosine similarity:
    # SELECT id, content, document_id, embedding <-> :query_embedding AS similarity
    # FROM chunk
    # WHERE document_id IN (SELECT id FROM document WHERE case_id = :case_id)
    # ORDER BY similarity
    # LIMIT :limit;

    # Using SQLModel with raw SQL for pgvector query
    # Note: SQLModel's ORM doesn't natively support pgvector operators like '<->' directly in `select()`,
    # so raw SQL is often necessary for vector search queries.
    try:
        # Ensure the query_embedding is a list of floats
        if not isinstance(query_embedding, list) or not all(isinstance(i, (int, float)) for i in query_embedding):
             raise ValueError("Query embedding is not a valid list of floats.")

        # Convert UUIDs to strings for the raw SQL query parameters
        case_id_str = str(case_id)
        query_embedding_str = str(query_embedding) # pgvector expects array literal format e.g., '[1.0, 2.0, ...]'

        # Construct the raw SQL query
        # Using parameterized query to prevent SQL injection
        sql_query = """
        SELECT
            chunk.id,
            chunk.content,
            chunk.document_id,
            chunk.embedding <-> :query_embedding AS similarity
        FROM chunk
        JOIN document ON chunk.document_id = document.id
        WHERE document.case_id = :case_id
        ORDER BY similarity
        LIMIT :limit;
        """

        # Execute the raw SQL query
        # The result will be a list of rows, where each row is a tuple or similar structure
        # We need to map this back to a list of Chunk objects or a custom result structure
        # For simplicity, let's return a list of dictionaries or a custom Pydantic model

        # Using session.exec(text(sql_query), params) is a way to execute raw SQL with parameters in SQLModel
        from sqlalchemy import text
        results = session.exec(
            text(sql_query),
            {"query_embedding": query_embedding_str, "case_id": case_id_str, "limit": limit}
        ).all()

        # Format the results
        # The results are tuples: (id, content, document_id, similarity)
        search_results = []
        for row in results:
            search_results.append({
                "chunk_id": row[0],
                "content": row[1],
                "document_id": row[2],
                "similarity": row[3]
            })

        print(f"Found {len(search_results)} relevant chunks for case {case_id}.")

        return search_results

    except Exception as e:
        # Log the error and raise an HTTPException
        print(f"Error during vector search for case {case_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Vector search failed: {e}")

# TODO: Add endpoints for listing, retrieving, updating, and deleting search results if needed
# (Less likely for search results, but possible for saved search queries or similar features)
