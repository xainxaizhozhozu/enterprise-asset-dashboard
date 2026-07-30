from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), comment="server, desktop, monitor, software, network")
    department = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    purchase_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", comment="active, inactive, maintenance, disposed")
    value = Column(Float, nullable=True)
    serial_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_deleted = Column(Integer, default=0)

    owner = relationship("User", back_populates="assets")
