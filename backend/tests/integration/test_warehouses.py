import pytest
from httpx import AsyncClient

BASE_AUTH = "/api/v1/auth"
BASE_WH = "/api/v1/warehouses"
BASE_LOC = "/api/v1/locations"

TEST_USER = {
    "email": "manager@coreinventory.com",
    "password": "Str0ngPass!",
    "full_name": "Test Manager",
    "role": "inventory_manager",
}


async def get_token(client: AsyncClient) -> str:
    await client.post(f"{BASE_AUTH}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE_AUTH}/jwt/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_warehouse(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        BASE_WH + "/",
        json={"name": "Main Warehouse", "short_code": "WH01", "address": "123 Main St"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["short_code"] == "WH01"


@pytest.mark.asyncio
async def test_duplicate_warehouse_code(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": "Main Warehouse", "short_code": "WH01"}
    await client.post(BASE_WH + "/", json=payload, headers=headers)
    resp = await client.post(BASE_WH + "/", json=payload, headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_warehouses(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(BASE_WH + "/", json={"name": "WH One", "short_code": "WH01"}, headers=headers)
    await client.post(BASE_WH + "/", json={"name": "WH Two", "short_code": "WH02"}, headers=headers)
    resp = await client.get(BASE_WH + "/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_update_warehouse(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    create = await client.post(BASE_WH + "/", json={"name": "Old Name", "short_code": "WH01"}, headers=headers)
    wh_id = create.json()["id"]
    resp = await client.patch(BASE_WH + f"/{wh_id}", json={"name": "New Name"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_create_location(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    wh = await client.post(BASE_WH + "/", json={"name": "Main WH", "short_code": "WH01"}, headers=headers)
    wh_id = wh.json()["id"]
    resp = await client.post(
        BASE_LOC + "/",
        json={"name": "Rack A", "short_code": "RA", "warehouse_id": wh_id},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["short_code"] == "RA"
    assert resp.json()["warehouse_name"] == "Main WH"


@pytest.mark.asyncio
async def test_location_invalid_warehouse(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        BASE_LOC + "/",
        json={"name": "Rack A", "short_code": "RA", "warehouse_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_warehouse_requires_auth(client: AsyncClient):
    resp = await client.get(BASE_WH + "/")
    assert resp.status_code == 401
