from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.user_repository import UserRepository
from schemas.user import UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_by_id(self, user_id: int):
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update(self, user_id: int, body: UserUpdate):
        return self.repo.update(user_id, body.model_dump(exclude_unset=True))
