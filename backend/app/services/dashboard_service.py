import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.operation import Operation, OperationStatus, OperationType
from app.models.product import Product
from app.models.stock_entry import StockEntry
from app.schemas.dashboard import DashboardKPIs, RecentActivity, StockAlertItem


class DashboardService:

    async def get_kpis(self, db: AsyncSession, user_id: uuid.UUID) -> DashboardKPIs:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # ── Products ──────────────────────────────────────────────────────────
        products_result = await db.execute(
            select(Product).options(selectinload(Product.stock_entries))
            .where(Product.is_active == True, Product.user_id == user_id)
        )
        products = products_result.scalars().all()

        total_products = len(products)
        out_of_stock_count = 0
        total_stock_value = Decimal("0")

        for p in products:
            qty = sum((e.quantity for e in p.stock_entries), Decimal("0"))
            total_stock_value += qty
            if qty == 0:
                out_of_stock_count += 1

        # ── Operations ────────────────────────────────────────────────────────
        pending_statuses = [OperationStatus.DRAFT, OperationStatus.CONFIRMED]

        async def count_ops(op_type: OperationType, statuses=None, since=None):
            stmt = select(func.count(Operation.id)).where(Operation.type == op_type, Operation.user_id == user_id)
            if statuses:
                stmt = stmt.where(Operation.status.in_(statuses))
            if since:
                stmt = stmt.where(Operation.created_at >= since)
            result = await db.execute(stmt)
            return result.scalar_one()

        pending_receipts = await count_ops(OperationType.RECEIPT, pending_statuses)
        pending_deliveries = await count_ops(OperationType.DELIVERY, pending_statuses)
        internal_scheduled = await count_ops(OperationType.INTERNAL, pending_statuses)
        receipts_today = await count_ops(OperationType.RECEIPT, since=today_start)
        deliveries_today = await count_ops(OperationType.DELIVERY, since=today_start)

        return DashboardKPIs(
            total_products=total_products,
            total_stock_value=total_stock_value,
            out_of_stock_count=out_of_stock_count,
            pending_receipts=pending_receipts,
            pending_deliveries=pending_deliveries,
            internal_transfers_scheduled=internal_scheduled,
            receipts_today=receipts_today,
            deliveries_today=deliveries_today,
        )

    async def get_recent_activity(self, db: AsyncSession, user_id: uuid.UUID, limit: int = 10) -> list[RecentActivity]:
        result = await db.execute(
            select(Operation)
            .options(
                selectinload(Operation.moves),
                selectinload(Operation.supplier_rel),
                selectinload(Operation.customer_rel),
            )
            .where(Operation.user_id == user_id)
            .order_by(Operation.created_at.desc())
            .limit(limit)
        )
        ops = result.scalars().all()
        return [
            RecentActivity(
                operation_id=str(op.id),
                reference=op.reference,
                type=op.type.value,
                status=op.status.value,
                party=(op.supplier_rel.name if op.supplier_rel else None) or (op.customer_rel.name if op.customer_rel else None) or op.supplier or op.customer,
                move_count=len(op.moves),
                created_at=op.created_at.isoformat(),
            )
            for op in ops
        ]

    async def get_stock_alerts(self, db: AsyncSession, user_id: uuid.UUID) -> list[StockAlertItem]:
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.stock_entries))
            .where(Product.is_active == True, Product.user_id == user_id)
            .order_by(Product.name)
        )
        products = result.scalars().all()
        alerts = []
        for p in products:
            qty = sum((e.quantity for e in p.stock_entries), Decimal("0"))
            if qty == 0:
                alerts.append(StockAlertItem(
                    product_id=str(p.id),
                    product_name=p.name,
                    sku=p.sku,
                    unit_of_measure=p.unit_of_measure,
                    total_stock=qty,
                    is_out_of_stock=True,
                ))
        return alerts


dashboard_service = DashboardService()
