from datetime import datetime

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Owner(Base):
    __tablename__ = "owners"

    owner_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    record_id: Mapped[str | None] = mapped_column(String(150), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(255), index=True)
    owner_type: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str | None] = mapped_column(String(100))
    id_number: Mapped[str | None] = mapped_column(String(100))
    uae_id_number: Mapped[str | None] = mapped_column(String(100))
    unified_number: Mapped[str | None] = mapped_column(String(100))
    passport_expiry_date: Mapped[datetime | None] = mapped_column(Date)
    birth_date: Mapped[datetime | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    contacts = relationship("Contact", back_populates="owner")
    ownership_history = relationship("OwnershipHistory", back_populates="owner")
    order_parties = relationship("OrderParty", back_populates="owner")