import pytest
from httpx import AsyncClient

from conftest import DEFAULT_PASSWORD, register_payload

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"


# ---- 회원가입 ----

async def test_register_success(client: AsyncClient):
    resp = await client.post(REGISTER, json=register_payload())

    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "user@example.com"
    assert body["username"] == "tester"
    assert body["phone"] == "010-0000-0000"
    assert body["is_active"] is True
    assert "id" in body and "created_at" in body


async def test_register_does_not_expose_password(client: AsyncClient):
    resp = await client.post(REGISTER, json=register_payload())

    assert "password" not in resp.json()
    assert "hashed_password" not in resp.json()


async def test_register_duplicate_email(client: AsyncClient, registered_user: dict):
    resp = await client.post(REGISTER, json=register_payload(registered_user["email"]))

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already registered"


@pytest.mark.parametrize("missing", ["email", "password", "username", "phone"])
async def test_register_missing_field(client: AsyncClient, missing: str):
    payload = register_payload()
    del payload[missing]

    resp = await client.post(REGISTER, json=payload)

    assert resp.status_code == 422


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"email": "not-an-email"}, id="invalid-email"),
        pytest.param({"password": "short"}, id="password-too-short"),
        pytest.param({"password": "a" * 73}, id="password-over-72-bytes"),
        pytest.param({"password": "가" * 25}, id="password-multibyte-over-72-bytes"),  # 75바이트
        pytest.param({"username": ""}, id="empty-username"),
        pytest.param({"phone": ""}, id="empty-phone"),
    ],
)
async def test_register_invalid_input(client: AsyncClient, overrides: dict):
    resp = await client.post(REGISTER, json=register_payload(**overrides))

    assert resp.status_code == 422


async def test_register_password_exactly_72_bytes(client: AsyncClient):
    resp = await client.post(REGISTER, json=register_payload(password="a" * 72))

    assert resp.status_code == 201


# ---- 로그인 ----

async def test_login_success(client: AsyncClient, registered_user: dict):
    resp = await client.post(
        LOGIN, json={"email": registered_user["email"], "password": DEFAULT_PASSWORD}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


@pytest.mark.parametrize(
    "email, password",
    [
        pytest.param("user@example.com", "wrong-password", id="wrong-password"),
        pytest.param("nobody@example.com", DEFAULT_PASSWORD, id="unknown-email"),
        pytest.param("user@example.com", "a" * 100, id="password-over-72-bytes"),
    ],
)
async def test_login_invalid_credentials(
    client: AsyncClient, registered_user: dict, email: str, password: str
):
    resp = await client.post(LOGIN, json={"email": email, "password": password})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


async def test_login_inactive_user(client: AsyncClient, registered_user: dict, db_engine):
    from sqlalchemy import text

    async with db_engine.begin() as conn:
        await conn.execute(
            text('UPDATE "user" SET is_active = false WHERE id = :id'),
            {"id": registered_user["id"]},
        )

    resp = await client.post(
        LOGIN, json={"email": registered_user["email"], "password": DEFAULT_PASSWORD}
    )

    assert resp.status_code == 401
