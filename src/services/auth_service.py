from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from repositories.user_repository import UserRepository
from schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def login(self, body: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_email(body.email)
        if not user or not verify_password(body.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return TokenResponse(access_token=create_access_token(user.id))

    def register(self, body: LoginRequest):
        if self.repo.get_by_email(body.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        return self.repo.create(
            email=body.email,
            hashed_password=hash_password(body.password),
        )
