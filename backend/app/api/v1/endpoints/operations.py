import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.operation import OperationStatus, OperationType
from app.models.user import User
from app.schemas.operation import (
    LedgerRead, OperationCreate, OperationListRead,
    OperationRead, OperationUpdate, StockMoveCreate,
)
from app.services.operation_service import operation_service

from fastapi.responses import StreamingResponse
from app.utils.pdf import generate_invoice_pdf

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("/{op_id}/pdf")
async def get_operation_pdf(
    op_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    op = await operation_service.get_by_id(db, op_id, user)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    pdf_buffer = generate_invoice_pdf(op)
    filename = f"invoice_{op.reference.replace('/', '_')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/", response_model=list[OperationListRead])
async def list_operations(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    op_type = None
    if type:
        try:
            op_type = OperationType(type.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid operation type: {type}")
            
    op_status = None
    if status:
        try:
            op_status = OperationStatus(status.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid operation status: {status}")

    return await operation_service.get_all(db, user=user, op_type=op_type, status=op_status, search=search)


@router.post("/", response_model=OperationRead, status_code=status.HTTP_201_CREATED)
async def create_operation(
    data: OperationCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        return await operation_service.create(db, data, user)
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@router.get("/ledger", response_model=list[LedgerRead])
async def get_ledger(
    product_id: Optional[uuid.UUID] = Query(None),
    location_id: Optional[uuid.UUID] = Query(None),
    type: Optional[OperationType] = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await operation_service.get_ledger(
        db, user=user, product_id=product_id, location_id=location_id, op_type=type, limit=limit
    )


@router.get("/{op_id}", response_model=OperationRead)
async def get_operation(
    op_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    op = await operation_service.get_by_id(db, op_id, user)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    return op


@router.patch("/{op_id}", response_model=OperationRead)
async def update_operation(
    op_id: uuid.UUID,
    data: OperationUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        return await operation_service.update(db, op_id, data, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{op_id}/moves", response_model=OperationRead)
async def add_move(
    op_id: uuid.UUID,
    data: StockMoveCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        return await operation_service.add_move(db, op_id, data, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{op_id}/moves/{move_id}", response_model=OperationRead)
async def remove_move(
    op_id: uuid.UUID,
    move_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        return await operation_service.remove_move(db, op_id, move_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{op_id}/confirm", response_model=OperationRead)
async def confirm_operation(
    op_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        return await operation_service.confirm(db, op_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{op_id}/validate", response_model=OperationRead)
async def validate_operation(
    op_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Validate a CONFIRMED operation → DONE.
    This is the step that actually moves stock and writes to the ledger.
    """
    try:
        return await operation_service.validate(db, op_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{op_id}/cancel", response_model=OperationRead)
async def cancel_operation(
    op_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        return await operation_service.cancel(db, op_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
