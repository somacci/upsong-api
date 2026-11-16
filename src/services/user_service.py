from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.user_repository import UserRepository
from schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update(self, user_id: int, body: UserUpdate) -> User:
        data = body.model_dump(exclude_unset=True)
        if "email" in data:
            existing = await self.repo.get_by_email(data["email"])
            if existing and existing.id != user_id:
                raise _email_conflict()
        try:
            user = await self.repo.update(user_id, data)
        except IntegrityError:
            raise _email_conflict()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user


def _email_conflict() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already registered",
    )
