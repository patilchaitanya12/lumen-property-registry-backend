from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Owner, Unit

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("")
def search(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
):
    pattern = f"%{q.strip()}%"

    owners = db.scalars(
        select(Owner)
        .where(
            or_(
                Owner.owner_id.ilike(pattern),
                Owner.name.ilike(pattern),
            )
        )
        .limit(10)
    ).all()

    units = db.scalars(
        select(Unit)
        .where(
            or_(
                Unit.unit_id.ilike(pattern),
                Unit.property_id.ilike(pattern),
                Unit.unit_code.ilike(pattern),
            )
        )
        .limit(10)
    ).all()

    return {
        "owners": [
            {
                "id": owner.owner_id,
                "name": owner.name,
                "type": "owner",
            }
            for owner in owners
        ],
        "units": [
            {
                "id": unit.unit_id,
                "unit_code": unit.unit_code,
                "type": "unit",
            }
            for unit in units
        ],
        "orders": [],
    }