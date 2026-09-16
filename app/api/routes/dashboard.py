from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Location,
    Order,
    Owner,
    OwnershipHistory,
    Unit,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db)):
    owners = db.scalar(select(func.count()).select_from(Owner)) or 0
    units = db.scalar(select(func.count()).select_from(Unit)) or 0
    locations = db.scalar(select(func.count()).select_from(Location)) or 0
    orders = db.scalar(select(func.count()).select_from(Order)) or 0
    ownerships = (
        db.scalar(
            select(func.count()).select_from(OwnershipHistory)
        )
        or 0
    )

    multi_owner_units = db.scalar(
        select(func.count()).select_from(
            select(OwnershipHistory.unit_id)
            .group_by(OwnershipHistory.unit_id)
            .having(
                func.count(
                    func.distinct(OwnershipHistory.owner_id)
                ) > 1
            )
            .subquery()
        )
    ) or 0

    return {
        "owners": owners,
        "units": units,
        "locations": locations,
        "orders": orders,
        "ownership_relationships": ownerships,
        "multi_owner_units": multi_owner_units,
    }