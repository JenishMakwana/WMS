import pytest
from httpx import AsyncClient

BASE_AUTH = "/api/v1/auth"
BASE_WH = "/api/v1/warehouses"
BASE_LOC = "/api/v1/locations"
BASE_PROD = "/api/v1/products"
BASE_OPS = "/api/v1/operations"

TEST_USER = {
    "email": "manager@coreinventory.com",
    "password": "Str0ngPass!",
    "full_name": "Test Manager",
    "role": "inventory_manager",
}

async def setup(client: AsyncClient):
    await client.post(f"{BASE_AUTH}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE_AUTH}/jwt/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    wh = await client.post(BASE_WH + "/", json={"name": "WH", "short_code": "WH1"}, headers=headers)
    loc = await client.post(BASE_LOC + "/", json={"name": "Rack A", "short_code": "RA", "warehouse_id": wh.json()["id"]}, headers=headers)
    prod = await client.post(BASE_PROD + "/", json={"name": "Steel Rod", "sku": "SR-001", "unit_of_measure": "kg"}, headers=headers)
    return headers, loc.json()["id"], prod.json()["id"]

@pytest.mark.asyncio
async def test_prevent_delivery_if_no_stock(client: AsyncClient):
    headers, loc_id, prod_id = await setup(client)

    # Attempt to deliver 10 units when we have 0
    op = await client.post(BASE_OPS + "/", json={
        "type": "delivery",
        "customer": "Client Co.",
        "src_location_id": loc_id,
        "moves": [{"product_id": prod_id, "demand_qty": "10"}],
    }, headers=headers)
    op_id = op.json()["id"]

    await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    
    # This should fail if we implement stock validation
    resp = await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)
    
    # Currently it probably returns 200 (Success) or 201
    assert resp.status_code == 400
    assert "Insufficient stock" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_prevent_internal_transfer_if_no_stock(client: AsyncClient):
    headers, loc_a, prod_id = await setup(client)
    
    wh = await client.get(BASE_WH + "/", headers=headers)
    wh_id = wh.json()[0]["id"]
    loc_b_resp = await client.post(BASE_LOC + "/", json={"name": "Rack B", "short_code": "RB", "warehouse_id": wh_id}, headers=headers)
    loc_b = loc_b_resp.json()["id"]

    # Attempt to transfer 10 units from Rack A to Rack B when Rack A has 0
    op = await client.post(BASE_OPS + "/", json={
        "type": "internal",
        "src_location_id": loc_a,
        "dest_location_id": loc_b,
        "moves": [{"product_id": prod_id, "demand_qty": "10"}],
    }, headers=headers)
    op_id = op.json()["id"]

    await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    
    resp = await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)
    
    assert resp.status_code == 400
    assert "Insufficient stock" in resp.json()["detail"]
