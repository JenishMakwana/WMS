import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    unit_of_measure = Column(String(50), nullable=False, default="pcs")  # pcs, kg, l, m, etc.
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    stock_entries = relationship("StockEntry", back_populates="product")
    user = relationship("User")

    def __repr__(self):
        return f"<Product {self.sku}>"
