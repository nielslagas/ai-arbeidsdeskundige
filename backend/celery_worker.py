from celery import Celery
import os
from dotenv import load_dotenv
from sqlmodel import Session, select, create_engine
from backend.models import Document
from backend.dependencies import supabase # Import supabase client from dependencies
import docx # For .docx parsing
import io # To read file content from bytes

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL") # Assuming DATABASE_URL is also in .env

if not DATABASE_URL:
     raise ValueError("DATABASE_URL must be set in the environment variables")

engine = create_engine(DATABASE_URL) # Database engine for Celery worker

def get_session():
    with Session(engine) as session:
        yield session

celery_app = Celery(
    "ad_rapport_generator",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_ignore_result=False,
    task_track_started=True,
)


celery_app = Celery(
    "ad_rapport_generator",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_ignore_result=False,
    task_track_started=True,
)

@celery_app.task
def process_document_mvp(document_id: str):
    """
    Celery task to process an uploaded document.
    (MVP: Placeholder for actual processing logic)
    """
    print(f"Processing document with ID: {document_id}")
    session = next(get_session()) # Get a database session

    try:
        # 1. Retrieve the Document object
        document = session.exec(select(Document).where(Document.id == document_id)).first()
        if not document:
            print(f"Document with ID {document_id} not found.")
            return

        # Update status to processing
        document.status = "processing"
        session.add(document)
        session.commit()
        session.refresh(document)
        print(f"Document {document_id} status updated to processing.")

        # 2. Download the document from Supabase Storage
        response = supabase.storage.from_('documents').download(document.storage_path)

        if response.get('error'):
            raise Exception(f"Supabase Storage download failed: {response['error']['message']}")

        file_content = response # response is the file content bytes

        # 3. Parse the document content
        file_extension = os.path.splitext(document.filename)[1].lower()
        content = ""

        if file_extension == ".docx":
            try:
                doc = docx.Document(io.BytesIO(file_content))
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                raise Exception(f"Error parsing DOCX file: {e}")
        elif file_extension == ".txt":
            try:
                content = file_content.decode('utf-8') # Assuming UTF-8 encoding
            except Exception as e:
                raise Exception(f"Error parsing TXT file: {e}")
        else:
            raise Exception(f"Unsupported file type: {file_extension}")

        print(f"Successfully parsed document {document_id}. Content length: {len(content)}")

        # Store parsed content
        document.parsed_content = content
        session.add(document)
        session.commit()
        session.refresh(document)
        print(f"Document {document_id} parsed content saved.")

        # 4. Implement Document Chunking (Task 2.2)
        # Split into paragraphs and create chunks
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()] # Split by double newline for paragraphs

        new_chunks = []
        # Simple paragraph-based chunking for now. More advanced methods (sliding window, sentence tokenization) could be used.
        for paragraph_text in paragraphs:
            # You might want to add logic here to split very long paragraphs or combine short ones
            if paragraph_text: # Ensure paragraph is not empty after stripping
                chunk = Chunk(document_id=document.id, content=paragraph_text, embedding=[]) # Placeholder for embedding
                new_chunks.append(chunk)

        if new_chunks:
            session.add_all(new_chunks)
            session.commit()
            # Refresh the session to get the newly created chunks with their IDs
            session.refresh(document)
            print(f"Created {len(new_chunks)} chunks for document {document_id}.")
        else:
            print(f"No chunks created for document {document_id}.")


        # 5. Implement Text Embedding (Task 2.3)
        # Using Supabase built-in embeddings via RPC.
        # Ensure your Supabase client is initialized correctly and the 'pgvector' extension is enabled in your database.
        # You might need to install the Supabase Python client with embeddings support: pip install supabase-py[embeddings]
        # The embedding model name might need to be configured (e.g., 'text-embedding-ada-002').

        # Retrieve the chunks again to ensure they are attached to the session
        chunks_to_embed = session.exec(select(Chunk).where(Chunk.document_id == document.id)).all()

        for chunk in chunks_to_embed:
            try:
                # Call Supabase embeddings API
                # The exact method name and parameters might vary based on the Supabase client version and setup.
                # This example assumes a 'generate_embedding' RPC function is set up in Supabase.
                # Alternatively, the Supabase client might have a dedicated embeddings method.
                # Refer to Supabase documentation for the exact API call.

                # Example using a hypothetical RPC call:
                # response = supabase.rpc('generate_embedding', {'input_text': chunk.content}).execute()
                # if response.data and response.data[0].get('embedding'):
                #     embedding_vector = response.data[0]['embedding']
                # else:
                #     raise Exception("Supabase embedding generation failed or returned no embedding.")

                # Call Supabase embeddings API using the 'generate_embedding' RPC
                # Ensure this RPC is set up in your Supabase project and uses the desired embedding model.
                # The input parameter name ('input_text') and output structure ('embedding') must match the RPC definition.
                response = supabase.rpc('generate_embedding', {'input_text': chunk.content}).execute()

                if response.data and response.data[0] and response.data[0].get('embedding'):
                    embedding_vector = response.data[0]['embedding']
                    chunk.embedding = embedding_vector
                    session.add(chunk)
                    session.commit()
                    session.refresh(chunk)
                    print(f"Saved embedding for chunk {chunk.id}.")
                else:
                    # Handle cases where embedding generation fails or returns no embedding
                    print(f"Supabase embedding generation failed or returned no embedding for chunk {chunk.id}. Response: {response}")
                    # Optionally, mark the chunk or document as failed or needing re-processing
                    # For now, we'll just log and continue

            except Exception as e:
                print(f"Error generating or saving embedding for chunk {chunk.id}: {e}")
                # Decide how to handle embedding failures - e.g., mark chunk as failed, log error, etc.
                # For now, we'll just print the error and continue

        # TODO: Implement Task 2.4 (Vector Search) - This is implemented in backend/routers/search.py
        # TODO: Implement Task 2.5 (Report Generation using RAG) - This is implemented in backend/routers/reports.py

        # Update status to completed after chunking and embedding (even if some embeddings failed)
        document.processing_status = "completed" # Use processing_status field
        session.add(document)
        session.commit()
        session.refresh(document)
        print(f"Document {document_id} processing_status updated to completed.")


    except Exception as e:
        # Update status to failed on error
        if 'document' in locals() and document:
            document.processing_status = "failed" # Use processing_status field
            # TODO: Store error details in the document model (add a field to Document model)
            session.add(document)
            session.commit()
            session.refresh(document)
            print(f"Document {document_id} processing failed: {e}")
        else:
             print(f"Document processing failed before retrieving document object: {e}")

    finally:
        session.close() # Close the session

# Example of how to run this worker:
# celery -A backend.celery_worker worker -l info
