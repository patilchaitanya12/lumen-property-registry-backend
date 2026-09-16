from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Location(Base):
    __tablename__ = "locations"

    location_id: Mapped[str] = mapped_column(String(150), primary_key=True)
    area_name: Mapped[str | None] = mapped_column(String(150))
    community: Mapped[str | None] = mapped_column(String(150), index=True)
    project: Mapped[str | None] = mapped_column(String(150))
    project_land: Mapped[str | None] = mapped_column(String(150))
    building_no: Mapped[str | None] = mapped_column(String(100))
    building_name: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    units = relationship("Unit", back_populates="location")
    orders = relationship("Order", back_populates="location")