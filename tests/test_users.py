from datetime import timedelta

from httpx import AsyncClient

from conftest import register_payload
from core.security import create_access_token

ME = "/api/v1/users/me"


# ---- 조회 ----

async def test_get_me(client: AsyncClient, auth_headers: dict, registered_user: dict):
    resp = await client.get(ME, headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == registered_user["id"]
    assert body["email"] == registered_user["email"]
    assert "hashed_password" not in body


async def test_get_me_without_token(client: AsyncClient):
    resp = await client.get(ME)

    assert resp.status_code == 401


async def test_get_me_invalid_token(client: AsyncClient):
    resp = await client.get(ME, headers={"Authorization": "Bearer not-a-jwt"})

    assert resp.status_code == 401


async def test_get_me_expired_token(client: AsyncClient, registered_user: dict):
    token = create_access_token(registered_user["id"], expires_delta=timedelta(seconds=-1))

    resp = await client.get(ME, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 401


async def test_get_me_deleted_user(client: AsyncClient):
    token = create_access_token(999999)

    resp = await client.get(ME, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 404


# ---- 수정 ----

async def test_update_me(client: AsyncClient, auth_headers: dict):
    resp = await client.patch(ME, headers=auth_headers, json={"username": "renamed"})

    assert resp.status_code == 200
    assert resp.json()["username"] == "renamed"
    # 보내지 않은 필드는 유지
    assert resp.json()["phone"] == "010-0000-0000"


async def test_update_me_email_to_own_email(
    client: AsyncClient, auth_headers: dict, registered_user: dict
):
    resp = await client.patch(ME, headers=auth_headers, json={"email": registered_user["email"]})

    assert resp.status_code == 200


async def test_update_me_email_conflict(client: AsyncClient, auth_headers: dict):
    other = await client.post("/api/v1/auth/register", json=register_payload("other@example.com"))
    assert other.status_code == 201

    resp = await client.patch(ME, headers=auth_headers, json={"email": "other@example.com"})

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already registered"


async def test_session_usable_after_conflict(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/auth/register", json=register_payload("other@example.com"))
    await client.patch(ME, headers=auth_headers, json={"email": "other@example.com"})

    resp = await client.get(ME, headers=auth_headers)

    assert resp.status_code == 200


async def test_update_me_deleted_user(client: AsyncClient):
    token = create_access_token(999999)

    resp = await client.patch(
        ME, headers={"Authorization": f"Bearer {token}"}, json={"username": "x"}
    )

    assert resp.status_code == 404


async def test_update_me_without_token(client: AsyncClient):
    resp = await client.patch(ME, json={"username": "x"})

    assert resp.status_code == 401
