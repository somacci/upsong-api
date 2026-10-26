from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user_id
from schemas.user import UserRead, UserUpdate
from services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_by_id(user_id)


@router.patch("/me", response_model=UserRead)
async def update_me(
    body: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).update(user_id, body)
