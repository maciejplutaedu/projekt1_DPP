from fastapi import FastAPI, HTTPException, Depends, Security, security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
from users_db import USERS_DB

app = FastAPI()

SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"

class LoginData(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    roles: list[str] = []

bearer_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
def login(data: LoginData):
    username = data.username
    password = data.password.encode("utf-8")

    user = USERS_DB.get(username)
    if not user or not bcrypt.checkpw(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": username,
        "roles": user["roles"],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users")
def create_user(user: UserCreate, token_data=Depends(verify_token)):
    if "ROLE_ADMIN" not in token_data.get("roles", []):
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    username = user.username
    password = user.password.encode("utf-8")

    if username in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
    USERS_DB[username] = {"password": hashed_pw, "roles": user.roles}

    return {"message": f"User '{username}' created successfully", "roles": user.roles}

@app.get("/user_details")
def user_details(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "username": payload.get("sub"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp")
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")