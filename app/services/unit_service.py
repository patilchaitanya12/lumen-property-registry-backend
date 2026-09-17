from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Location, Owner, OwnershipHistory, Unit
from app.services.dashboard_service import get_dashboard_stats


def list_units(
    db: Session,
    query: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    stmt = select(Unit)

    if query:
        pattern = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Unit.unit_id.ilike(pattern),
                Unit.property_id.ilike(pattern),
                Unit.unit_code.ilike(pattern),
                Unit.unit_number.ilike(pattern),
            )
        )

    if query:
        total = db.scalar(
            select(func.count()).select_from(
                stmt.order_by(None).subquery()
            )
        ) or 0
    else:
        total = get_dashboard_stats()["units"]

    units = db.scalars(
        stmt
        .order_by(Unit.unit_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "unit_id": unit.unit_id,
                "property_id": unit.property_id,
                "unit_code": unit.unit_code,
                "unit_number": unit.unit_number,
                "location_id": unit.location_id,
                "property_type": unit.property_type,
                "size": unit.size,
            }
            for unit in units
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def get_unit(
    db: Session,
    unit_id: str,
) -> dict | None:
    unit = db.get(Unit, unit_id)

    if unit is None:
        return None

    location = (
        db.get(Location, unit.location_id)
        if unit.location_id
        else None
    )

    owners = db.execute(
        select(Owner, OwnershipHistory)
        .join(
            OwnershipHistory,
            OwnershipHistory.owner_id == Owner.owner_id,
        )
        .where(
            OwnershipHistory.unit_id == unit_id
        )
        .order_by(
            OwnershipHistory.start_date.desc().nullslast()
        )
    ).all()

    return {
        "unit_id": unit.unit_id,
        "property_id": unit.property_id,
        "unit_code": unit.unit_code,
        "unit_number": unit.unit_number,
        "property_type": unit.property_type,
        "size": unit.size,
        "dm_no": unit.dm_no,
        "dm_sub_no": unit.dm_sub_no,
        "land_sub_number": unit.land_sub_number,
        "location": (
            {
                "location_id": location.location_id,
                "community": location.community,
                "building_name": location.building_name,
            }
            if location
            else None
        ),
        "owners": [
            {
                "owner_id": owner.owner_id,
                "name": owner.name,
                "owner_type": owner.owner_type,
                "start_date": history.start_date,
                "end_date": history.end_date,
            }
            for owner, history in owners
        ],
    }


def get_unit_owners(
    db: Session,
    unit_id: str,
) -> list[dict] | None:
    if db.get(Unit, unit_id) is None:
        return None

    rows = db.execute(
        select(Owner, OwnershipHistory)
        .join(
            OwnershipHistory,
            OwnershipHistory.owner_id == Owner.owner_id,
        )
        .where(
            OwnershipHistory.unit_id == unit_id
        )
    ).all()

    return [
        {
            "owner_id": owner.owner_id,
            "name": owner.name,
            "owner_type": owner.owner_type,
            "start_date": history.start_date,
            "end_date": history.end_date,
        }
        for owner, history in rows
    ]


def get_unit_history(
    db: Session,
    unit_id: str,
) -> list[dict] | None:
    if db.get(Unit, unit_id) is None:
        return None

    rows = db.execute(
        select(OwnershipHistory, Owner)
        .join(
            Owner,
            Owner.owner_id == OwnershipHistory.owner_id,
        )
        .where(
            OwnershipHistory.unit_id == unit_id
        )
        .order_by(
            OwnershipHistory.start_date.asc().nullslast()
        )
    ).all()

    return [
        {
            "history_id": history.ownership_history_id,
            "owner_id": owner.owner_id,
            "owner_name": owner.name,
            "start_date": history.start_date,
            "end_date": history.end_date,
            "source_order_id": history.source_order_id,
        }
        for history, owner in rows
    ]