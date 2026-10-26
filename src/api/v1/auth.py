from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.auth import LoginRequest, TokenResponse
from services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(body)


@router.post("/register", status_code=201)
async def register(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(body)
