from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class OrderParty(Base):
    __tablename__ = "order_parties"

    order_party_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("owners.owner_id"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_row_id: Mapped[str | None] = mapped_column(
        String(100),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    order = relationship(
        "Order",
        back_populates="parties",
    )

    owner = relationship(
        "Owner",
        back_populates="order_parties",
    )