import pytest
from httpx import AsyncClient

BASE_AUTH = "/api/v1/auth"
BASE_WH = "/api/v1/warehouses"
BASE_LOC = "/api/v1/locations"
BASE_PROD = "/api/v1/products"
BASE_OPS = "/api/v1/operations"
BASE_DASH = "/api/v1/dashboard"
BASE_ADJ = "/api/v1/adjustments"

TEST_USER = {
    "email": "manager@coreinventory.com",
    "password": "Str0ngPass!",
    "full_name": "Test Manager",
    "role": "inventory_manager",
}


async def bootstrap(client):
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
async def test_kpis_empty(client: AsyncClient):
    headers, _, _ = await bootstrap(client)
    resp = await client.get(BASE_DASH + "/kpis", headers=headers)
    assert resp.status_code == 200
    kpis = resp.json()
    assert kpis["total_products"] == 1
    assert kpis["out_of_stock_count"] == 1
    assert kpis["pending_receipts"] == 0


@pytest.mark.asyncio
async def test_kpis_after_receipt(client: AsyncClient):
    headers, loc_id, prod_id = await bootstrap(client)

    op = await client.post(BASE_OPS + "/", json={
        "type": "receipt", "dest_location_id": loc_id,
        "moves": [{"product_id": prod_id, "demand_qty": "50"}],
    }, headers=headers)
    op_id = op.json()["id"]

    # KPI: pending_receipts = 1 (draft)
    kpis = (await client.get(BASE_DASH + "/kpis", headers=headers)).json()
    assert kpis["pending_receipts"] == 1

    # Validate
    await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)

    kpis = (await client.get(BASE_DASH + "/kpis", headers=headers)).json()
    assert kpis["pending_receipts"] == 0
    assert kpis["out_of_stock_count"] == 0
    assert float(kpis["total_stock_value"]) == 50.0


@pytest.mark.asyncio
async def test_recent_activity(client: AsyncClient):
    headers, loc_id, prod_id = await bootstrap(client)
    await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT", "dest_location_id": loc_id,
        "moves": [{"product_id": prod_id, "demand_qty": "10"}],
    }, headers=headers)
    resp = await client.get(BASE_DASH + "/activity", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["type"] == "RECEIPT"


@pytest.mark.asyncio
async def test_stock_adjustment(client: AsyncClient):
    headers, loc_id, prod_id = await bootstrap(client)

    # Receive 100
    op = await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT", "dest_location_id": loc_id,
        "moves": [{"product_id": prod_id, "demand_qty": "100"}],
    }, headers=headers)
    op_id = op.json()["id"]
    await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)

    # Adjust to 85 (simulating 15 units damaged)
    resp = await client.post(BASE_ADJ + "/", json={
        "lines": [{"product_id": prod_id, "location_id": loc_id, "counted_qty": "85", "note": "Damaged items removed"}],
        "notes": "Monthly physical count",
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["reference"].startswith("ADJ/")
    assert resp.json()["status"] == "DONE"

    # Verify stock is now 85
    prod = await client.get(f"{BASE_PROD}/{prod_id}", headers=headers)
    assert float(prod.json()["total_stock"]) == 85.0


@pytest.mark.asyncio
async def test_adjustment_no_change(client: AsyncClient):
    """Adjustment with counted_qty == current qty should produce no moves."""
    headers, loc_id, prod_id = await bootstrap(client)

    op = await client.post(BASE_OPS + "/", json={
        "type": "receipt", "dest_location_id": loc_id,
        "moves": [{"product_id": prod_id, "demand_qty": "50"}],
    }, headers=headers)
    op_id = op.json()["id"]
    await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)

    resp = await client.post(BASE_ADJ + "/", json={
        "lines": [{"product_id": prod_id, "location_id": loc_id, "counted_qty": "50"}],
    }, headers=headers)
    assert resp.status_code == 201
    assert len(resp.json()["moves"]) == 0  # no delta
