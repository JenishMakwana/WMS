from decimal import Decimal
from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    total_products: int
    total_stock_value: Decimal  # sum of all on-hand quantities
    out_of_stock_count: int
    pending_receipts: int        # operations: receipt + draft/confirmed
    pending_deliveries: int      # operations: delivery + draft/confirmed
    internal_transfers_scheduled: int
    receipts_today: int
    deliveries_today: int


class RecentActivity(BaseModel):
    operation_id: str
    reference: str
    type: str
    status: str
    party: str | None           # supplier or customer
    move_count: int
    created_at: str


class StockAlertItem(BaseModel):
    product_id: str
    product_name: str
    sku: str
    unit_of_measure: str
    total_stock: Decimal
    is_out_of_stock: bool
