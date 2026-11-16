from pydantic import BaseModel, EmailStr, Field, field_validator

from core.security import BCRYPT_MAX_BYTES


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=1, max_length=20)

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, v: str) -> str:
        if len(v.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"Password must be at most {BCRYPT_MAX_BYTES} bytes")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
