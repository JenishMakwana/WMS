import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class StockLedger(Base):
    """
    Append-only ledger. One row per product/location/operation.
    Never update or delete — only insert.
    qty_change: positive = stock in, negative = stock out.
    """
    __tablename__ = "stock_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    operation_id = Column(UUID(as_uuid=True), ForeignKey("operations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    qty_change = Column(Numeric(12, 3), nullable=False)   # + or -
    balance_after = Column(Numeric(12, 3), nullable=False) # running total at this location

    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product")
    location = relationship("Location")
    operation = relationship("Operation")
    user = relationship("User")

    def __repr__(self):
        return f"<Ledger product={self.product_id} change={self.qty_change}>"
