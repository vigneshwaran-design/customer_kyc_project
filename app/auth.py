from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Demo credentials
fake_users = {
    "admin": {"username": "admin", "password": "secret"}
}

def create_access_token(data: dict, expires_delta=None):
    encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def login_user(form: OAuth2PasswordRequestForm = Depends()):
    user = fake_users.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(status_code=401, detail="Invalid login")

    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = data.get("sub")

        if username not in fake_users:
            raise HTTPException(status_code=401, detail="Invalid token")

        return username

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
