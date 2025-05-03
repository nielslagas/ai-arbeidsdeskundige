from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import List
from backend.models import Document, Case
from backend.dependencies import get_session, get_current_user, supabase # Import dependencies from backend.dependencies
import uuid
import os
from backend.celery_worker import celery_app
from sqlalchemy.exc import SQLAlchemyError # Import SQLAlchemyError

print("--- Loading backend/routers/documents.py ---") # Debugging: Check if module is loaded

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=Document)
def create_document(document: Document, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Create a new document for a case owned by the current user."""
    # Verify the case exists and belongs to the current user
    user_uuid = uuid.UUID(current_user.id)
    case = session.exec(select(Case).where(Case.id == document.case_id, Case.user_id == user_uuid)).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found or does not belong to the current user")

    session.add(document)
    session.commit()
    session.refresh(document)
    return document

@router.get("/case/{case_id}", response_model=List[Document])
def read_documents_for_case(case_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Retrieve all documents for a specific case owned by the current user."""
    user_uuid = uuid.UUID(current_user.id)
    # Verify the case exists and belongs to the current user
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == user_uuid)).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found or does not belong to the current user")

    documents = session.exec(select(Document).where(Document.case_id == case_id)).all()
    return documents

@router.get("/{document_id}", response_model=Document)
def read_document(document_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Retrieve a specific document by ID for a case owned by the current user."""
    user_uuid = uuid.UUID(current_user.id)
    # Select the document and join with Case to verify ownership
    document = session.exec(
        select(Document)
        .join(Case)
        .where(Document.id == document_id, Case.user_id == user_uuid)
    ).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or does not belong to a case owned by the current user")
    return document

@router.put("/{document_id}", response_model=Document)
def update_document(document_id: uuid.UUID, document_update: Document, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Update a specific document by ID for a case owned by the current user."""
    user_uuid = uuid.UUID(current_user.id)
    # Select the document and join with Case to verify ownership
    document = session.exec(
        select(Document)
        .join(Case)
        .where(Document.id == document_id, Case.user_id == user_uuid)
    ).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or does not belong to a case owned by the current user")

    # Update fields, excluding id, case_id, uploaded_at
    update_data = document_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key not in ["id", "case_id", "uploaded_at"]:
            setattr(document, key, value)

    session.add(document)
    session.commit()
    session.refresh(document)
    return document

@router.delete("/{document_id}", response_model=dict)
def delete_document(document_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Delete a specific document by ID for a case owned by the current user."""
    user_uuid = uuid.UUID(current_user.id)
    # Select the document and join with Case to verify ownership
    document = session.exec(
        select(Document)
        .join(Case)
        .where(Document.id == document_id, Case.user_id == user_uuid)
    ).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or does not belong to a case owned by the current user")

    session.delete(document)
    session.commit()
    return {"ok": True}

@router.post("/{case_id}/upload_mvp")
async def upload_document_mvp(case_id: uuid.UUID, file: UploadFile = File(...), session: Session = Depends(get_session)): # Added back session dependency
    """Upload a document (docx/txt) for a case, save to Supabase Storage, create DB record, and trigger Celery task."""
    print("--- Entering upload_document_mvp function ---") # Debugging: Check if function is entered
    print("upload_document_mvp function entered") # Added for debugging
    try:
        # Temporarily removed user_uuid and case verification

        # Validate file type (basic check)
        allowed_types = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only .docx and .txt are allowed.")

        # Generate a unique filename for Supabase Storage
        file_extension = os.path.splitext(file.filename)[1]
        # Using a placeholder for user_uuid in storage path for now
        storage_filename = f"{uuid.uuid4()}{file_extension}"
        storage_path = f"temp/{case_id}/{storage_filename}" # Store under temp/case_id

        # Read the file content in chunks to avoid loading large files into memory
        file_content = await file.read()

        # Upload file to Supabase Storage
        response = supabase.storage.from_('documents').upload(storage_path, file_content)

        # If no exception was raised, the upload was successful.
        print(f"Received filename: {file.filename}") # Debugging: Check the received filename

        # Add print statements to inspect values before DB insertion
        print(f"Value of file.filename: {file.filename}")
        print(f"Value of storage_path: {storage_path}")
        print(f"Value of file.content_type: {file.content_type}")

        # Alternative way to create and populate the Document object
        new_document = Document()
        new_document.case_id = case_id
        # new_document.user_id = user_uuid # user_uuid is not available yet
        new_document.file_name = file.filename
        new_document.file_path = storage_path
        new_document.file_type = file.content_type
        new_document.processing_status = "uploaded"
        # uploaded_at will be set by default_factory
        # parsed_content defaults to None

        # Print the new_document object before adding to session
        print(f"New document object before session.add: {new_document}")

        session.add(new_document) # Add the new document object
        session.commit()
        session.refresh(new_document) # Refresh the new document object

        # Temporarily skip Celery task
        # celery_app.send_task('backend.celery_worker.process_document_mvp', args=[str(document.id)]) # document is not created

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Document upload test successful (Celery task skipped)"})

    except Exception as e:
        print(f"--- An error occurred in upload_document_mvp ---")
        print(f"Error type: {type(e)}")
        print(f"Error message: {e}")
        # If it's a SQLAlchemy error, print more details
        if isinstance(e, SQLAlchemyError):
            print(f"SQLAlchemy Error details: {e.orig}")
            if hasattr(e.orig, 'pgerror'):
                print(f"PostgreSQL Error details: {e.orig.pgerror}")

        session.rollback() # Rollback DB transaction if upload fails
        # TODO: Clean up uploaded file from Supabase Storage if DB record creation fails (need to implement cleanup logic)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload document: {e}")
