from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.models import User
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "borrower"
    age: int
    gender: Literal["male", "female"]
    education: Literal["High School or Below", "college", "Bachelor Degree", "Master or Above"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def get_client_ip(request: Request) -> str | None:
    """Render (and most hosting platforms) sit behind a reverse proxy,
    so request.client.host is the proxy's internal IP, not the real
    visitor's — every user would appear to share one IP, silently
    breaking the fraud detection's shared-IP signal. X-Forwarded-For
    holds the real chain of IPs when present; its first entry is the
    original client."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/signup")
def signup(request: SignupRequest, http_request: Request, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.password),
        role=request.role,
        age=request.age,
        gender=request.gender,
        education=request.education,
        signup_ip=get_client_ip(http_request),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}