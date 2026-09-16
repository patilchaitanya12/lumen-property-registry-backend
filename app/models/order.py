from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(
        String(150),
        primary_key=True,
    )

    source_regis: Mapped[str | None] = mapped_column(
        String(150),
        index=True,
    )

    unit_id: Mapped[str | None] = mapped_column(
        ForeignKey("units.unit_id"),
        index=True,
    )

    location_id: Mapped[str | None] = mapped_column(
        ForeignKey("locations.location_id"),
        index=True,
    )

    procedure_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    procedure_value: Mapped[str | None] = mapped_column(
        String(255),
    )

    transaction_date: Mapped[date | None] = mapped_column(
        Date,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    unit = relationship(
        "Unit",
        back_populates="orders",
    )

    location = relationship(
        "Location",
        back_populates="orders",
    )

    parties = relationship(
        "OrderParty",
        back_populates="order",
    )