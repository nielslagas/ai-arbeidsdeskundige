from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from typing import Annotated

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL") # Assuming DATABASE_URL is also in .env

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment variables")

if not DATABASE_URL:
     raise ValueError("DATABASE_URL must be set in the environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Database setup
engine = create_engine(DATABASE_URL, echo=True) # echo=True for development to see SQL queries

def get_session():
    with Session(engine) as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # We will implement token endpoint later

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Verify the token with Supabase
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
