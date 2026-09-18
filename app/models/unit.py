from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Unit(Base):
    __tablename__ = "units"

    unit_id: Mapped[str] = mapped_column(String(150), primary_key=True)
    property_id: Mapped[str | None] = mapped_column(String(150), unique=True, index=True)
    unit_code: Mapped[str | None] = mapped_column(String(150), index=True)
    unit_number: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
    )

    location_id: Mapped[str | None] = mapped_column(
        ForeignKey("locations.location_id"), index=True
    )

    property_type: Mapped[str | None] = mapped_column(String(100))
    size: Mapped[float | None] = mapped_column(Numeric(14, 2))
    dm_no: Mapped[str | None] = mapped_column(String(100))
    dm_sub_no: Mapped[str | None] = mapped_column(String(100))
    land_sub_number: Mapped[str | None] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    location = relationship("Location", back_populates="units")
    orders = relationship("Order", back_populates="unit")
    ownership_history = relationship(
        "OwnershipHistory", back_populates="unit"
    )