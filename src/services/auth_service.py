from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password, verify_password
from models.user import User
from repositories.user_repository import UserRepository
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def login(self, body: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(body.email)
        if not user or not user.is_active or not verify_password(body.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return TokenResponse(access_token=create_access_token(user.id))

    async def register(self, body: RegisterRequest) -> User:
        if await self.repo.get_by_email(body.email):
            raise _email_conflict()
        try:
            return await self.repo.create(
                email=body.email,
                username=body.username,
                phone=body.phone,
                hashed_password=hash_password(body.password),
            )
        except IntegrityError:
            # 동시 가입 요청으로 사전 확인을 통과한 경우 (email unique 제약 위반)
            raise _email_conflict()


def _email_conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already registered",
    )
