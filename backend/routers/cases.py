from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from backend.models import Case
from backend.dependencies import get_session, get_current_user # Import dependencies from backend.dependencies
import uuid

router = APIRouter(prefix="/cases", tags=["cases"])

@router.post("/", response_model=Case)
def create_case(case: Case, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Create a new case."""
    # Ensure the case is associated with the current user
    case.user_id = uuid.UUID(current_user.id)
    session.add(case)
    session.commit()
    session.refresh(case)
    return case

@router.get("/", response_model=List[Case])
def read_cases(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Retrieve all cases for the current user."""
    user_uuid = uuid.UUID(current_user.id)
    cases = session.exec(select(Case).where(Case.user_id == user_uuid)).all()
    return cases

@router.get("/{case_id}", response_model=Case)
def read_case(case_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Retrieve a specific case by ID for the current user."""
    user_uuid = uuid.UUID(current_user.id)
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == user_uuid)).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=Case)
def update_case(case_id: uuid.UUID, case_update: Case, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Update a specific case by ID for the current user."""
    user_uuid = uuid.UUID(current_user.id)
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == user_uuid)).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Update fields, excluding id, user_id, and created_at
    update_data = case_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key not in ["id", "user_id", "created_at"]:
            setattr(case, key, value)

    session.add(case)
    session.commit()
    session.refresh(case)
    return case

@router.delete("/{case_id}", response_model=dict)
def delete_case(case_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Delete a specific case by ID for the current user."""
    user_uuid = uuid.UUID(current_user.id)
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == user_uuid)).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    session.delete(case)
    session.commit()
    return {"ok": True}
