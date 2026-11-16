from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 실행 위치(cwd)와 무관하게 프로젝트 루트의 .env.local을 읽도록 절대경로 사용
# (.env는 autoenv 셸 스크립트 전용이므로 앱 설정은 .env.local에 둔다)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Upsong API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://soma@localhost/fastapi"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env.local", env_file_encoding="utf-8")


settings = Settings()
