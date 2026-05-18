import pytest
from httpx import AsyncClient

BASE_AUTH = "/api/v1/auth"
BASE_WH = "/api/v1/warehouses"
BASE_LOC = "/api/v1/locations"
BASE_PROD = "/api/v1/products"
BASE_CAT = "/api/v1/categories"

TEST_USER = {
    "email": "manager@coreinventory.com",
    "password": "Str0ngPass!",
    "full_name": "Test Manager",
    "role": "inventory_manager",
}


async def setup(client: AsyncClient):
    """Register user, create warehouse + location, return token + location_id."""
    await client.post(f"{BASE_AUTH}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE_AUTH}/jwt/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    wh = await client.post(BASE_WH + "/", json={"name": "Main WH", "short_code": "WH01"}, headers=headers)
    wh_id = wh.json()["id"]
    loc = await client.post(
        BASE_LOC + "/",
        json={"name": "Rack A", "short_code": "RA", "warehouse_id": wh_id},
        headers=headers,
    )
    return headers, loc.json()["id"]


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient):
    headers, loc_id = await setup(client)
    resp = await client.post(
        BASE_PROD + "/",
        json={"name": "Steel Rod", "sku": "SR-001", "unit_of_measure": "kg"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["sku"] == "SR-001"
    assert resp.json()["total_stock"] == "0"


@pytest.mark.asyncio
async def test_create_product_with_initial_stock(client: AsyncClient):
    headers, loc_id = await setup(client)
    resp = await client.post(
        BASE_PROD + "/",
        json={
            "name": "Steel Rod",
            "sku": "SR-001",
            "unit_of_measure": "kg",
            "quantity": "100",
            "initial_location_id": loc_id,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert float(resp.json()["total_stock"]) == 100.0
    assert len(resp.json()["stock_by_location"]) == 1


@pytest.mark.asyncio
async def test_duplicate_sku(client: AsyncClient):
    headers, _ = await setup(client)
    payload = {"name": "Steel Rod", "sku": "SR-001", "unit_of_measure": "kg"}
    await client.post(BASE_PROD + "/", json=payload, headers=headers)
    resp = await client.post(BASE_PROD + "/", json=payload, headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_products_search(client: AsyncClient):
    headers, _ = await setup(client)
    await client.post(BASE_PROD + "/", json={"name": "Steel Rod", "sku": "SR-001", "unit_of_measure": "kg"}, headers=headers)
    await client.post(BASE_PROD + "/", json={"name": "Copper Wire", "sku": "CW-001", "unit_of_measure": "m"}, headers=headers)
    resp = await client.get(BASE_PROD + "/?search=steel", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["sku"] == "SR-001"


@pytest.mark.asyncio
async def test_create_and_list_categories(client: AsyncClient):
    headers, _ = await setup(client)
    await client.post(BASE_CAT + "/", json={"name": "Raw Materials"}, headers=headers)
    await client.post(BASE_CAT + "/", json={"name": "Finished Goods"}, headers=headers)
    resp = await client.get(BASE_CAT + "/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient):
    headers, _ = await setup(client)
    create = await client.post(
        BASE_PROD + "/", json={"name": "Steel Rod", "sku": "SR-001", "unit_of_measure": "kg"}, headers=headers
    )
    prod_id = create.json()["id"]
    resp = await client.patch(
        BASE_PROD + f"/{prod_id}",
        json={"name": "New Name"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_product_not_found(client: AsyncClient):
    headers, _ = await setup(client)
    resp = await client.get(BASE_PROD + "/00000000-0000-0000-0000-000000000000", headers=headers)
    assert resp.status_code == 404
