from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Owner, Unit


def search_registry(
    db: Session,
    query: str,
) -> dict:
    pattern = f"%{query.strip()}%"

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