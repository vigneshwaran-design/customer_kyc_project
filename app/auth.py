from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import hashlib
import bcrypt

from app.models import User
from app.database import get_db

# JWT
SECRET_KEY = "customer_kyc_#2025#%"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------- PASSWORD HASHING (No 72-byte limit) ----------------
def hash_password(password: str) -> str:
    """Hash any-length password: SHA256 → bcrypt"""
    sha256_hash = hashlib.sha256(password.encode()).digest()
    hashed = bcrypt.hashpw(sha256_hash, bcrypt.gensalt())
    return hashed.decode()


def verify_password(raw_password: str, hashed_password: str) -> bool:
    sha256_hash = hashlib.sha256(raw_password.encode()).digest()
    return bcrypt.checkpw(sha256_hash, hashed_password.encode())


# ---------------- CREATE JWT TOKEN ----------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- LOGIN ----------------
def login_user(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form.username).first()

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}


# ---------------- VERIFY TOKEN ----------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user

    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
