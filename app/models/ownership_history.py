from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class OwnershipHistory(Base):
    __tablename__ = "ownership_history"

    ownership_history_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    unit_id: Mapped[str] = mapped_column(
        ForeignKey("units.unit_id"), nullable=False, index=True
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("owners.owner_id"), nullable=False, index=True
    )

    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)

    source_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("orders.order_id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    unit = relationship("Unit", back_populates="ownership_history")
    owner = relationship("Owner", back_populates="ownership_history")
    source_order = relationship("Order")