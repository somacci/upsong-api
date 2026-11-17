"""테스트 공통 설정.

- 개발 DB와 분리된 테스트 전용 DB를 사용한다.
  기본값: DATABASE_URL의 DB 이름 뒤에 `_test`를 붙인 DB (예: fastapi → fastapi_test)
  변경: 환경변수 TEST_DATABASE_URL
- 테스트 DB가 없으면 자동 생성하고, 세션 시작 시 테이블을 새로 만든다.
- 각 테스트가 끝날 때마다 모든 테이블을 비운다.
"""
import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import models.user  # noqa: F401 — Base.metadata에 테이블 등록
from core.config import settings
from core.database import get_db
from main import app
from models.base import Base

_dev_url = make_url(settings.database_url)
TEST_DATABASE_URL = make_url(
    os.environ.get("TEST_DATABASE_URL")
    or _dev_url.set(database=f"{_dev_url.database}_test").render_as_string(hide_password=False)
)

# 개발 DB를 실수로 지우지 않도록 방어
assert TEST_DATABASE_URL.database != _dev_url.database or "TEST_DATABASE_URL" in os.environ, (
    "테스트 DB가 개발 DB와 같습니다. TEST_DATABASE_URL을 확인하세요."
)


async def _prepare_test_database() -> None:
    # 1) 테스트 DB가 없으면 생성 (관리용 postgres DB에 접속)
    admin = create_async_engine(
        TEST_DATABASE_URL.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with admin.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DATABASE_URL.database},
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{TEST_DATABASE_URL.database}"'))
    await admin.dispose()

    # 2) 현재 모델 기준으로 테이블을 새로 생성
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _test_database() -> None:
    asyncio.run(_prepare_test_database())


@pytest.fixture
async def db_engine():
    # 테스트마다 이벤트 루프가 달라지므로 커넥션 풀을 쓰지 않는다
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine
    async with engine.begin() as conn:
        tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    await engine.dispose()


@pytest.fixture
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---- 공용 헬퍼 ----

DEFAULT_PASSWORD = "password1234"


def register_payload(email: str = "user@example.com", **overrides) -> dict:
    return {
        "email": email,
        "password": DEFAULT_PASSWORD,
        "username": "tester",
        "phone": "010-0000-0000",
        **overrides,
    }


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    payload = register_payload()
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    return {**resp.json(), "password": payload["password"]}


@pytest.fixture
async def auth_headers(client: AsyncClient, registered_user: dict) -> dict:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
