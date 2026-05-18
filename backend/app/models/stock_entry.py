import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class StockEntry(Base):
    """
    Tracks on-hand quantity for a specific product at a specific location.
    One row per (product, location) pair — updated on every validated operation.
    """
    __tablename__ = "stock_entries"
    __table_args__ = (
        UniqueConstraint("product_id", "location_id", name="uq_stock_product_location"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="stock_entries")
    location = relationship("Location", back_populates="stock_entries")

    def __repr__(self):
        return f"<StockEntry product={self.product_id} location={self.location_id} qty={self.quantity}>"
