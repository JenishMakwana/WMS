import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.location import Location
from app.models.operation import Operation, OperationStatus, OperationType, StockMove
from app.models.product import Product
from app.models.stock_entry import StockEntry
from app.models.stock_ledger import StockLedger
from app.models.user import User
from app.schemas.operation import (
    LedgerRead, OperationCreate, OperationListRead,
    OperationRead, OperationUpdate, StockMoveRead,
)


def _ref_prefix(op_type: OperationType) -> str:
    return {
        OperationType.RECEIPT: "REC",
        OperationType.DELIVERY: "DEL",
        OperationType.INTERNAL: "INT",
        OperationType.ADJUSTMENT: "ADJ"
    }[op_type]


async def _next_reference(db: AsyncSession, op_type: OperationType) -> str:
    prefix = _ref_prefix(op_type)
    
    # Find the maximum reference for this type to avoid duplicates after deletions
    stmt = (
        select(Operation.reference)
        .where(Operation.type == op_type)
        .order_by(Operation.reference.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    last_ref = result.scalar_one_or_none()
    
    if not last_ref:
        return f"{prefix}/00001"
    
    try:
        # Expected format: "PREFIX/00001"
        last_num_str = last_ref.split("/")[-1]
        last_num = int(last_num_str)
        new_num = last_num + 1
    except (ValueError, IndexError):
        # Fallback if the format is not as expected
        res = await db.execute(
            select(func.count(Operation.id)).where(Operation.type == op_type)
        )
        new_num = res.scalar_one() + 1
        
    return f"{prefix}/{new_num:05d}"


def _build_move_read(m: StockMove) -> StockMoveRead:
    return StockMoveRead(
        id=m.id,
        product_id=m.product_id,
        product_name=m.product.name if m.product else "",
        product_sku=m.product.sku if m.product else "",
        product_uom=m.product.unit_of_measure if m.product else "",
        demand_qty=m.demand_qty,
        done_qty=m.done_qty,
        src_location_id=m.src_location_id,
        src_location_name=m.src_location.name if m.src_location else None,
        dest_location_id=m.dest_location_id,
        dest_location_name=m.dest_location.name if m.dest_location else None,
    )


def _build_op_read(op: Operation) -> OperationRead:
    return OperationRead(
        id=op.id,
        reference=op.reference,
        type=op.type,
        status=op.status,
        supplier=op.supplier,
        customer=op.customer,
        supplier_id=op.supplier_id,
        customer_id=op.customer_id,
        supplier_name=op.supplier_rel.name if op.supplier_rel else None,
        customer_name=op.customer_rel.name if op.customer_rel else None,
        supplier_address=op.supplier_rel.address if op.supplier_rel else None,
        customer_address=op.customer_rel.address if op.customer_rel else None,
        notes=op.notes,
        src_location_id=op.src_location_id,
        src_location_name=op.src_location.name if op.src_location else None,
        src_warehouse_name=op.src_location.warehouse.name if op.src_location and op.src_location.warehouse else None,
        src_warehouse_address=op.src_location.warehouse.address if op.src_location and op.src_location.warehouse else None,
        dest_location_id=op.dest_location_id,
        dest_location_name=op.dest_location.name if op.dest_location else None,
        dest_warehouse_name=op.dest_location.warehouse.name if op.dest_location and op.dest_location.warehouse else None,
        dest_warehouse_address=op.dest_location.warehouse.address if op.dest_location and op.dest_location.warehouse else None,
        scheduled_date=op.scheduled_date,
        validated_at=op.validated_at,
        user_id=op.user_id,
        created_by_name=op.created_by.full_name if op.created_by else None,
        created_at=op.created_at,
        moves=[_build_move_read(m) for m in op.moves],
    )


async def _get_or_create_stock_entry(
    db: AsyncSession, product_id: uuid.UUID, location_id: uuid.UUID
) -> StockEntry:
    result = await db.execute(
        select(StockEntry)
        .options(selectinload(StockEntry.location))
        .where(
            StockEntry.product_id == product_id,
            StockEntry.location_id == location_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        entry = StockEntry(product_id=product_id, location_id=location_id, quantity=Decimal("0"))
        db.add(entry)
        await db.flush()
    return entry


async def _apply_ledger(
    db: AsyncSession,
    product_id: uuid.UUID,
    location_id: uuid.UUID,
    qty_change: Decimal,
    operation_id: uuid.UUID,
    note: Optional[str] = None,
) -> None:
    entry = await _get_or_create_stock_entry(db, product_id, location_id)
    entry.quantity += qty_change
    ledger = StockLedger(
        product_id=product_id,
        location_id=location_id,
        operation_id=operation_id,
        qty_change=qty_change,
        balance_after=entry.quantity,
        note=note,
    )
    db.add(ledger)


class OperationService:

    async def _load_op(self, db: AsyncSession, op_id: uuid.UUID) -> Optional[Operation]:
        result = await db.execute(
            select(Operation)
            .options(
                selectinload(Operation.moves).selectinload(StockMove.product),
                selectinload(Operation.moves).selectinload(StockMove.src_location),
                selectinload(Operation.moves).selectinload(StockMove.dest_location),
                selectinload(Operation.src_location).selectinload(Location.warehouse),
                selectinload(Operation.dest_location).selectinload(Location.warehouse),
                selectinload(Operation.created_by),
                selectinload(Operation.supplier_rel),
                selectinload(Operation.customer_rel),
            )
            .where(Operation.id == op_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        user: User,
        op_type: Optional[OperationType] = None,
        status: Optional[OperationStatus] = None,
        search: Optional[str] = None,
    ) -> list[OperationListRead]:
        stmt = (
            select(Operation)
            .options(
                selectinload(Operation.src_location).selectinload(Location.warehouse),
                selectinload(Operation.dest_location).selectinload(Location.warehouse),
                selectinload(Operation.moves),
                selectinload(Operation.supplier_rel),
                selectinload(Operation.customer_rel),
            )
            .order_by(Operation.created_at.desc())
        )
        
        # Data isolation: Only see operations belonging to this owner/user
        stmt = stmt.where(Operation.user_id == user.id)
        
        # Role-based restriction: staff only see what they created
        if user.role == "warehouse_staff":
            stmt = stmt.where(Operation.created_by_id == user.id)

        if op_type:
            stmt = stmt.where(Operation.type == op_type)
        if status:
            stmt = stmt.where(Operation.status == status)
        if search:
            stmt = stmt.where(Operation.reference.ilike(f"%{search}%"))

        result = await db.execute(stmt)
        ops = result.scalars().all()

        return [
            OperationListRead(
                id=op.id,
                reference=op.reference,
                type=op.type,
                status=op.status,
                supplier=op.supplier,
                customer=op.customer,
                supplier_name=op.supplier_rel.name if op.supplier_rel else None,
                customer_name=op.customer_rel.name if op.customer_rel else None,
                supplier_address=op.supplier_rel.address if op.supplier_rel else None,
                customer_address=op.customer_rel.address if op.customer_rel else None,
                src_location_name=op.src_location.name if op.src_location else None,
                dest_location_name=op.dest_location.name if op.dest_location else None,
                src_warehouse_name=op.src_location.warehouse.name if op.src_location and op.src_location.warehouse else None,
                dest_warehouse_name=op.dest_location.warehouse.name if op.dest_location and op.dest_location.warehouse else None,
                scheduled_date=op.scheduled_date,
                validated_at=op.validated_at,
                user_id=op.user_id,
                created_at=op.created_at,
                move_count=len(op.moves),
            )
            for op in ops
        ]

    async def get_by_id(self, db: AsyncSession, op_id: uuid.UUID, user: User) -> Optional[OperationRead]:
        op = await self._load_op(db, op_id)
        if not op:
            return None
        
        # Check ownership
        if op.user_id != user.id:
            return None
            
        return _build_op_read(op)

    async def create(
        self, db: AsyncSession, data: OperationCreate, user: User
    ) -> OperationRead:
        reference = await _next_reference(db, data.type)
        op = Operation(
            reference=reference,
            type=data.type,
            status=OperationStatus.DRAFT,
            supplier=data.supplier,
            customer=data.customer,
            supplier_id=data.supplier_id,
            customer_id=data.customer_id,
            notes=data.notes,
            src_location_id=data.src_location_id,
            dest_location_id=data.dest_location_id,
            scheduled_date=data.scheduled_date,
            user_id=user.id,
            created_by_id=user.id,
        )
        db.add(op)
        await db.flush()

        for move_data in data.moves:
            move = StockMove(
                operation_id=op.id,
                product_id=move_data.product_id,
                demand_qty=move_data.demand_qty,
                src_location_id=move_data.src_location_id or data.src_location_id,
                dest_location_id=move_data.dest_location_id or data.dest_location_id,
            )
            db.add(move)

        await db.commit()
        return _build_op_read(await self._load_op(db, op.id))

    async def add_move(
        self, db: AsyncSession, op_id: uuid.UUID, move_data, user: User
    ) -> OperationRead:
        op = await self._load_op(db, op_id)
        if not op or op.user_id != user.id:
            raise ValueError("Operation not found")
        if op.status != OperationStatus.DRAFT:
            raise ValueError("Can only add lines to a DRAFT operation")
        move = StockMove(
            operation_id=op.id,
            product_id=move_data.product_id,
            demand_qty=move_data.demand_qty,
            src_location_id=move_data.src_location_id or op.src_location_id,
            dest_location_id=move_data.dest_location_id or op.dest_location_id,
        )
        db.add(move)
        await db.commit()
        return _build_op_read(await self._load_op(db, op.id))

    async def remove_move(self, db: AsyncSession, op_id: uuid.UUID, move_id: uuid.UUID, user: User) -> OperationRead:
        op = await self._load_op(db, op_id)
        if not op or op.user_id != user.id:
            raise ValueError("Operation not found")
        if op.status != OperationStatus.DRAFT:
            raise ValueError("Can only remove lines from a DRAFT operation")
        move = next((m for m in op.moves if m.id == move_id), None)
        if move:
            await db.delete(move)
            await db.commit()
        return _build_op_read(await self._load_op(db, op.id))

    async def confirm(self, db: AsyncSession, op_id: uuid.UUID, user: User) -> OperationRead:
        """DRAFT → CONFIRMED."""
        op = await self._load_op(db, op_id)
        if not op or op.user_id != user.id:
            raise ValueError("Operation not found")
        if op.status != OperationStatus.DRAFT:
            raise ValueError(f"Cannot confirm operation in status '{op.status}'")
        if not op.moves:
            raise ValueError("Cannot confirm an operation with no product lines")
        op.status = OperationStatus.CONFIRMED
        await db.commit()
        return _build_op_read(await self._load_op(db, op.id))

    async def validate(self, db: AsyncSession, op_id: uuid.UUID, user: User) -> OperationRead:
        """
        CONFIRMED → DONE.
        Applies stock movements and validates availability.
        """
        op = await self._load_op(db, op_id)
        if not op or op.user_id != user.id:
            raise ValueError("Operation not found")
        if op.status != OperationStatus.CONFIRMED:
            raise ValueError(f"Cannot validate operation in status '{op.status}'")

        # ── Stock Availability Check ──────────────────────────────────────────
        if op.type in [OperationType.DELIVERY, OperationType.INTERNAL]:
            for move in op.moves:
                src = move.src_location_id or op.src_location_id
                if not src:
                    raise ValueError(f"Source location missing for move of {move.product.name}")
                
                # Check current on-hand in this location
                entry = await _get_or_create_stock_entry(db, move.product_id, src)
                if entry.quantity < move.demand_qty:
                    raise ValueError(
                        f"Insufficient stock for '{move.product.name}' at '{entry.location.name}'. "
                        f"Need {move.demand_qty:.2f}, but only {entry.quantity:.2f} available."
                    )

        # ── Apply Movements ───────────────────────────────────────────────────
        for move in op.moves:
            qty = move.demand_qty
            move.done_qty = qty

            if op.type == OperationType.RECEIPT:
                dest = move.dest_location_id or op.dest_location_id
                await _apply_ledger(db, move.product_id, dest, qty, op.id, f"Receipt {op.reference}")

            elif op.type == OperationType.DELIVERY:
                src = move.src_location_id or op.src_location_id
                await _apply_ledger(db, move.product_id, src, -qty, op.id, f"Delivery {op.reference}")

            elif op.type == OperationType.INTERNAL:
                src = move.src_location_id or op.src_location_id
                dest = move.dest_location_id or op.dest_location_id
                await _apply_ledger(db, move.product_id, src, -qty, op.id, f"Transfer out {op.reference}")
                await _apply_ledger(db, move.product_id, dest, qty, op.id, f"Transfer in {op.reference}")

            elif op.type == OperationType.ADJUSTMENT:
                dest = move.dest_location_id or op.dest_location_id
                await _apply_ledger(db, move.product_id, dest, qty, op.id, f"Adjustment {op.reference}")

        op.status = OperationStatus.DONE
        op.validated_at = datetime.now(timezone.utc)
        await db.commit()

        # Broadcast low-stock alerts over WebSocket after commit
        await self._broadcast_low_stock_alerts(db, op)

        return _build_op_read(await self._load_op(db, op.id))

    async def _broadcast_low_stock_alerts(self, db: AsyncSession, op: Operation) -> None:
        from app.utils.ws_manager import manager
        from app.models.stock_entry import StockEntry

        product_ids = list({m.product_id for m in op.moves})
        for pid in product_ids:
            result = await db.execute(
                select(StockEntry).where(StockEntry.product_id == pid)
            )
            entries = result.scalars().all()
            total = sum((e.quantity for e in entries), Decimal("0"))

            prod_result = await db.execute(
                select(Product).where(Product.id == pid)
            )
            product = prod_result.scalar_one_or_none()
            if not product:
                continue

            if total == 0:
                await manager.broadcast({
                    "type": "out_of_stock",
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "sku": product.sku,
                    "qty": 0.0,
                    "is_out_of_stock": True,
                })

    async def cancel(self, db: AsyncSession, op_id: uuid.UUID, user: User) -> OperationRead:
        op = await self._load_op(db, op_id)
        if not op or op.user_id != user.id:
            raise ValueError("Operation not found")
        if op.status == OperationStatus.DONE:
            raise ValueError("Cannot cancel a completed operation")
        op.status = OperationStatus.CANCELLED
        await db.commit()
        return _build_op_read(await self._load_op(db, op.id))

    async def update(
        self, db: AsyncSession, op_id: uuid.UUID, data: OperationUpdate, user: User
    ) -> OperationRead:
        op = await self._load_op(db, op_id)
        if not op or op.user_id != user.id:
            raise ValueError("Operation not found")
        if op.status != OperationStatus.DRAFT:
            raise ValueError("Can only update DRAFT operations")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(op, field, value)
        await db.commit()
        return _build_op_read(await self._load_op(db, op.id))

    # ── Ledger ────────────────────────────────────────────────────────────────

    async def get_ledger(
        self,
        db: AsyncSession,
        user: User,
        product_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None,
        op_type: Optional[OperationType] = None,
        limit: int = 100,
    ) -> list[LedgerRead]:
        stmt = (
            select(StockLedger)
            .options(
                selectinload(StockLedger.product),
                selectinload(StockLedger.location).selectinload(Location.warehouse),
                selectinload(StockLedger.operation),
            )
            .join(Operation, isouter=True) # Join to filter by user_id
            .where(
                (Operation.id == None) | (Operation.user_id == user.id)
            )
            .order_by(StockLedger.created_at.desc())
            .limit(limit)
        )
        if product_id:
            stmt = stmt.where(StockLedger.product_id == product_id)
        if location_id:
            stmt = stmt.where(StockLedger.location_id == location_id)
        if op_type:
            stmt = stmt.where(
                StockLedger.operation_id.in_(
                    select(Operation.id).where(Operation.type == op_type)
                )
            )

        result = await db.execute(stmt)
        rows = result.scalars().all()

        return [
            LedgerRead(
                id=r.id,
                product_id=r.product_id,
                product_name=r.product.name,
                product_sku=r.product.sku,
                location_id=r.location_id,
                location_name=r.location.name,
                warehouse_name=r.location.warehouse.name,
                operation_id=r.operation_id,
                operation_reference=r.operation.reference if r.operation else None,
                operation_type=r.operation.type if r.operation else None,
                qty_change=r.qty_change,
                balance_after=r.balance_after,
                note=r.note,
                created_at=r.created_at,
            )
            for r in rows
        ]


operation_service = OperationService()
