from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.auth import LoginRequest, TokenResponse
from services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(body)


@router.post("/register", status_code=201)
def register(body: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(body)
