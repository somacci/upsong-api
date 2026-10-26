from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository
from schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_by_id(self, user_id: int):
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update(self, user_id: int, body: UserUpdate):
        return await self.repo.update(user_id, body.model_dump(exclude_unset=True))
