from fastapi import FastAPI
from app.database import Base, engine
from app.auth import login_user
from app.schemas import Token
from app.routers import upload

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer KYC Upload")

# --- Authentication Route ---
@app.post("/auth/token", response_model=Token)
def login(form=Depends(login_user)):
    return form

# --- Upload Router ---
app.include_router(upload.router)
