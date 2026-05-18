import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, DateTime, Enum, ForeignKey,
    Numeric, String, Text, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class OperationType(str, PyEnum):
    RECEIPT = "RECEIPT"
    DELIVERY = "DELIVERY"
    INTERNAL = "INTERNAL"
    ADJUSTMENT = "ADJUSTMENT"


class OperationStatus(str, PyEnum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Operation(Base):
    """
    Header record for any inventory operation:
    receipt, delivery, internal transfer, or adjustment.
    """
    __tablename__ = "operations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference = Column(String(60), nullable=False, unique=True, index=True)
    type = Column(Enum(OperationType, name="operationtype"), nullable=False, index=True)
    status = Column(
        Enum(OperationStatus, name="operationstatus"),
        nullable=False,
        default=OperationStatus.DRAFT,
        index=True,
    )

    # Parties
    supplier = Column(String(200), nullable=True)   # receipts (legacy)
    customer = Column(String(200), nullable=True)   # deliveries (legacy)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Locations (source → destination)
    src_location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    dest_location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)

    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    moves = relationship("StockMove", back_populates="operation", cascade="all, delete-orphan")
    src_location = relationship("Location", foreign_keys=[src_location_id])
    dest_location = relationship("Location", foreign_keys=[dest_location_id])
    user = relationship("User", foreign_keys=[user_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    supplier_rel = relationship("Supplier", foreign_keys=[supplier_id])
    customer_rel = relationship("Customer", foreign_keys=[customer_id])

    def __repr__(self):
        return f"<Operation {self.reference} [{self.type}/{self.status}]>"


class StockMove(Base):
    """
    One line in an operation — product + quantity being moved.
    When validated, updates StockEntry balances.
    """
    __tablename__ = "stock_moves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_id = Column(UUID(as_uuid=True), ForeignKey("operations.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    demand_qty = Column(Numeric(12, 3), nullable=False)   # requested
    done_qty = Column(Numeric(12, 3), nullable=True)      # actual (filled on validate)

    src_location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    dest_location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    operation = relationship("Operation", back_populates="moves")
    product = relationship("Product")
    src_location = relationship("Location", foreign_keys=[src_location_id])
    dest_location = relationship("Location", foreign_keys=[dest_location_id])

    def __repr__(self):
        return f"<StockMove product={self.product_id} qty={self.demand_qty}>"
