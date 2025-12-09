from fastapi import FastAPI, Depends
from app.database import Base, engine
from app.auth import login_user
from app.schemas import Token
from app.routers import upload, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer KYC Upload System")

# Login
@app.post("/auth/login", response_model=Token)
def login(form=Depends(login_user)):
    return form

# Routers
app.include_router(users.router)
app.include_router(upload.router)
