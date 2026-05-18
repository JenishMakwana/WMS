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


async def bootstrap(client: AsyncClient):
    """Create user, warehouse, two locations, one product. Return headers + ids."""
    await client.post(f"{BASE_AUTH}/register", json=TEST_USER)
    resp = await client.post(
        f"{BASE_AUTH}/jwt/login",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    wh = await client.post(BASE_WH + "/", json={"name": "Main WH", "short_code": "WH01"}, headers=headers)
    wh_id = wh.json()["id"]

    loc_a = await client.post(BASE_LOC + "/", json={"name": "Rack A", "short_code": "RA", "warehouse_id": wh_id}, headers=headers)
    loc_b = await client.post(BASE_LOC + "/", json={"name": "Rack B", "short_code": "RB", "warehouse_id": wh_id}, headers=headers)

    prod = await client.post(BASE_PROD + "/", json={"name": "Steel Rod", "sku": "SR-001", "unit_of_measure": "kg"}, headers=headers)

    return headers, loc_a.json()["id"], loc_b.json()["id"], prod.json()["id"]


@pytest.mark.asyncio
async def test_create_receipt(client: AsyncClient):
    headers, loc_a, loc_b, prod_id = await bootstrap(client)
    resp = await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT",
        "supplier": "ACME Supplies",
        "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "100"}],
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["reference"].startswith("REC/")
    assert data["status"] == "DRAFT"
    assert len(data["moves"]) == 1


@pytest.mark.asyncio
async def test_receipt_full_flow(client: AsyncClient):
    """Draft → Confirm → Validate → stock increases."""
    headers, loc_a, loc_b, prod_id = await bootstrap(client)

    # Create
    op = await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT",
        "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "50"}],
    }, headers=headers)
    op_id = op.json()["id"]

    # Confirm
    confirmed = await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    assert confirmed.json()["status"] == "CONFIRMED"

    # Validate
    validated = await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)
    assert validated.json()["status"] == "DONE"

    # Check stock
    prod = await client.get(f"{BASE_PROD}/{prod_id}", headers=headers)
    assert float(prod.json()["total_stock"]) == 50.0


@pytest.mark.asyncio
async def test_delivery_reduces_stock(client: AsyncClient):
    headers, loc_a, loc_b, prod_id = await bootstrap(client)

    # First receive 100
    op_in = await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT",
        "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "100"}],
    }, headers=headers)
    await client.post(f"{BASE_OPS}/{op_in.json()['id']}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_in.json()['id']}/validate", headers=headers)

    # Then deliver 30
    op_out = await client.post(BASE_OPS + "/", json={
        "type": "DELIVERY",
        "customer": "Client Co.",
        "src_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "30"}],
    }, headers=headers)
    await client.post(f"{BASE_OPS}/{op_out.json()['id']}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_out.json()['id']}/validate", headers=headers)

    prod = await client.get(f"{BASE_PROD}/{prod_id}", headers=headers)
    assert float(prod.json()["total_stock"]) == 70.0


@pytest.mark.asyncio
async def test_internal_transfer_moves_stock(client: AsyncClient):
    headers, loc_a, loc_b, prod_id = await bootstrap(client)

    # Receive 80 at Rack A
    op_in = await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT", "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "80"}],
    }, headers=headers)
    await client.post(f"{BASE_OPS}/{op_in.json()['id']}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_in.json()['id']}/validate", headers=headers)

    # Transfer 40 from Rack A to Rack B
    op_tr = await client.post(BASE_OPS + "/", json={
        "type": "INTERNAL",
        "src_location_id": loc_a,
        "dest_location_id": loc_b,
        "moves": [{"product_id": prod_id, "demand_qty": "40"}],
    }, headers=headers)
    await client.post(f"{BASE_OPS}/{op_tr.json()['id']}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_tr.json()['id']}/validate", headers=headers)

    prod = await client.get(f"{BASE_PROD}/{prod_id}", headers=headers)
    assert float(prod.json()["total_stock"]) == 80.0  # total unchanged
    locs = {s["location_name"]: float(s["quantity"]) for s in prod.json()["stock_by_location"]}
    assert locs["Rack A"] == 40.0
    assert locs["Rack B"] == 40.0


@pytest.mark.asyncio
async def test_cancel_operation(client: AsyncClient):
    headers, loc_a, loc_b, prod_id = await bootstrap(client)
    op = await client.post(BASE_OPS + "/", json={
        "type": "RECEIPT", "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "10"}],
    }, headers=headers)
    op_id = op.json()["id"]
    cancelled = await client.post(f"{BASE_OPS}/{op_id}/cancel", headers=headers)
    assert cancelled.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_cannot_validate_draft(client: AsyncClient):
    headers, loc_a, _, prod_id = await bootstrap(client)
    op = await client.post(BASE_OPS + "/", json={
        "type": "receipt", "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "10"}],
    }, headers=headers)
    resp = await client.post(f"{BASE_OPS}/{op.json()['id']}/validate", headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ledger_entries_created(client: AsyncClient):
    headers, loc_a, _, prod_id = await bootstrap(client)
    op = await client.post(BASE_OPS + "/", json={
        "type": "receipt", "dest_location_id": loc_a,
        "moves": [{"product_id": prod_id, "demand_qty": "25"}],
    }, headers=headers)
    op_id = op.json()["id"]
    await client.post(f"{BASE_OPS}/{op_id}/confirm", headers=headers)
    await client.post(f"{BASE_OPS}/{op_id}/validate", headers=headers)

    ledger = await client.get(f"{BASE_OPS}/ledger?product_id={prod_id}", headers=headers)
    assert ledger.status_code == 200
    assert len(ledger.json()) == 1
    assert float(ledger.json()[0]["qty_change"]) == 25.0
    assert float(ledger.json()[0]["balance_after"]) == 25.0
