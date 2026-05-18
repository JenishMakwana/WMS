from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.operation import Operation, OperationStatus, OperationType, StockMove
from app.models.stock_entry import StockEntry
from app.models.user import User
from app.schemas.adjustment import AdjustmentCreate
from app.schemas.operation import OperationRead
from app.services.operation_service import (
    _apply_ledger, _build_op_read, _next_reference, operation_service
)
from datetime import datetime, timezone

router = APIRouter(prefix="/adjustments", tags=["adjustments"])


@router.post("/", response_model=OperationRead, status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    data: AdjustmentCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Create and immediately validate a stock adjustment.
    For each line: compares counted_qty with current balance and applies the delta.
    """
    reference = await _next_reference(db, OperationType.ADJUSTMENT)
    op = Operation(
        reference=reference,
        type=OperationType.ADJUSTMENT,
        status=OperationStatus.CONFIRMED,
        notes=data.notes,
        user_id=user.id,
        created_by_id=user.id,
    )
    db.add(op)
    await db.flush()

    for line in data.lines:
        # Get current stock at this location
        result = await db.execute(
            select(StockEntry).where(
                StockEntry.product_id == line.product_id,
                StockEntry.location_id == line.location_id,
            )
        )
        entry = result.scalar_one_or_none()
        current_qty = entry.quantity if entry else Decimal("0")
        delta = line.counted_qty - current_qty

        if delta == 0:
            continue  # no change needed

        # Add move line
        move = StockMove(
            operation_id=op.id,
            product_id=line.product_id,
            demand_qty=abs(delta),
            done_qty=abs(delta),
            dest_location_id=line.location_id,
        )
        db.add(move)

        # Apply to ledger (delta can be + or -)
        note = line.note or f"Adjustment {reference}: {current_qty} → {line.counted_qty}"
        await _apply_ledger(db, line.product_id, line.location_id, delta, op.id, note)

    op.status = OperationStatus.DONE
    op.validated_at = datetime.now(timezone.utc)
    await db.commit()

    loaded = await operation_service._load_op(db, op.id)
    if not loaded:
        raise HTTPException(status_code=500, detail="Failed to load adjustment after creation")
    return _build_op_read(loaded)
