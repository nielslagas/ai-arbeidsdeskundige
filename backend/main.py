from fastapi import FastAPI, Depends, Request, status # Add Request, status
from sqlmodel import SQLModel # Keep SQLModel for create_db_and_tables
from backend.routers import cases # Import the cases router
from backend.routers import documents # Import the documents router
from backend.routers import search # Import the search router
from backend.routers import reports # Import the reports router
from backend.dependencies import get_current_user, engine # Import dependencies and engine
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Include routers
print("--- Including cases router ---")
app.include_router(cases.router)
print("--- Including documents router ---") # Debugging: Check if documents router is being included
app.include_router(documents.router)
print("--- Including search router ---")
app.include_router(search.router)
print("--- Including reports router ---")
app.include_router(reports.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Request validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.get("/")
async def read_root():
    return {"message": "AD-Rapport Generator AI Backend"}

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}
