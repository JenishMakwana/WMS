import pytest
from httpx import AsyncClient

BASE = "/api/v1/auth"

TEST_USER = {
    "email": "manager@coreinventory.com",
    "password": "Str0ngPass!",
    "full_name": "Test Manager",
    "role": "inventory_manager",
}


async def register_and_login(client: AsyncClient) -> str:
    """Helper: register a user and return the JWT access token."""
    await client.post(f"{BASE}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE}/jwt/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(f"{BASE}/register", json=TEST_USER)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == TEST_USER["email"]
    assert body["full_name"] == TEST_USER["full_name"]
    assert body["role"] == TEST_USER["role"]
    assert "password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(f"{BASE}/register", json=TEST_USER)
    resp = await client.post(f"{BASE}/register", json=TEST_USER)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(f"{BASE}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE}/jwt/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(f"{BASE}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE}/jwt/login",
        data={"username": TEST_USER["email"], "password": "wrongpass"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    token = await register_and_login(client)
    resp = await client.get(
        f"{BASE}/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == TEST_USER["email"]
    assert resp.json()["role"] == TEST_USER["role"]


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    resp = await client.get(f"{BASE}/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_forgot_password_returns_202(client: AsyncClient):
    await client.post(f"{BASE}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE}/forgot-password", json={"email": TEST_USER["email"]}
    )
    # fastapi-users always returns 202 to avoid email enumeration
    assert resp.status_code == 202
