from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Owner(Base):
    __tablename__ = "owners"

    owner_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    record_id: Mapped[str | None] = mapped_column(String(150), unique=True)

    # Core identity
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    normalized_name: Mapped[str | None] = mapped_column(
        String(255),
        index=True,
    )
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(100))

    # Classification
    owner_type: Mapped[str | None] = mapped_column(String(50))
    vip_tier: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[str | None] = mapped_column(String(30))
    gender_source: Mapped[str | None] = mapped_column(String(50))

    # Source / provenance
    source_community: Mapped[str | None] = mapped_column(String(255))
    source_file: Mapped[str | None] = mapped_column(String(500))

    # Geographic / identity information
    country: Mapped[str | None] = mapped_column(String(100))
    id_number: Mapped[str | None] = mapped_column(String(100))
    uae_id_number: Mapped[str | None] = mapped_column(String(100))
    unified_number: Mapped[str | None] = mapped_column(String(100))
    passport_expiry_date: Mapped[datetime | None] = mapped_column(Date)
    birth_date: Mapped[datetime | None] = mapped_column(Date)

    # Portfolio information
    property_count: Mapped[int | None] = mapped_column(Integer)
    communities_owned: Mapped[int | None] = mapped_column(Integer)
    community_list: Mapped[str | None] = mapped_column(Text)
    buildings_list: Mapped[str | None] = mapped_column(Text)

    is_multi_property: Mapped[bool | None] = mapped_column(Boolean)
    is_portfolio_investor: Mapped[bool | None] = mapped_column(Boolean)
    has_cross_community: Mapped[bool | None] = mapped_column(Boolean)
    portfolio_tier: Mapped[str | None] = mapped_column(String(100))

    has_plot: Mapped[bool | None] = mapped_column(Boolean)
    has_apartment: Mapped[bool | None] = mapped_column(Boolean)
    has_villa: Mapped[bool | None] = mapped_column(Boolean)

    # Contact reachability
    is_reachable: Mapped[bool | None] = mapped_column(Boolean)

    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    contacts = relationship("Contact", back_populates="owner")
    ownership_history = relationship(
        "OwnershipHistory",
        back_populates="owner",
    )
    order_parties = relationship(
        "OrderParty",
        back_populates="owner",
    )
