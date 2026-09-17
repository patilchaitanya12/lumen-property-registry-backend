from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Contact, Owner, OwnershipHistory, Unit


def list_owners(
    db: Session,
    query: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    stmt = select(Owner)

    if query:
        pattern = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Owner.owner_id.ilike(pattern),
                Owner.name.ilike(pattern),
            )
        )

    if query:
        total = db.scalar(
            select(func.count()).select_from(
                stmt.order_by(None).subquery()
            )
        ) or 0
    else:
        total = db.scalar(
            select(func.count()).select_from(Owner)
        ) or 0

    owners = db.scalars(
        stmt
        .order_by(Owner.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "owner_id": owner.owner_id,
                "record_id": owner.record_id,
                "name": owner.name,
                "owner_type": owner.owner_type,
                "country": owner.country,
            }
            for owner in owners
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def get_owner(
    db: Session,
    owner_id: str,
) -> dict | None:
    owner = db.get(Owner, owner_id)

    if owner is None:
        return None

    property_count = db.scalar(
        select(
            func.count(
                func.distinct(OwnershipHistory.unit_id)
            )
        ).where(
            OwnershipHistory.owner_id == owner_id
        )
    ) or 0

    contacts = db.scalars(
        select(Contact)
        .where(Contact.owner_id == owner_id)
        .order_by(Contact.is_primary.desc())
    ).all()

    return {
        "owner_id": owner.owner_id,
        "record_id": owner.record_id,
        "name": owner.name,
        "normalized_name": owner.normalized_name,
        "owner_type": owner.owner_type,
        "country": owner.country,
        "id_number": owner.id_number,
        "uae_id_number": owner.uae_id_number,
        "unified_number": owner.unified_number,
        "property_count": property_count,
        "contacts": [
            {
                "contact_id": contact.contact_id,
                "type": contact.contact_type,
                "value": contact.contact_value,
                "is_primary": contact.is_primary,
            }
            for contact in contacts
        ],
    }


def get_owner_units(
    db: Session,
    owner_id: str,
) -> list[dict] | None:
    if db.get(Owner, owner_id) is None:
        return None

    rows = db.execute(
        select(Unit, OwnershipHistory)
        .join(
            OwnershipHistory,
            OwnershipHistory.unit_id == Unit.unit_id,
        )
        .where(
            OwnershipHistory.owner_id == owner_id
        )
        .order_by(Unit.unit_id)
    ).all()

    return [
        {
            "unit_id": unit.unit_id,
            "property_id": unit.property_id,
            "unit_code": unit.unit_code,
            "unit_number": unit.unit_number,
            "location_id": unit.location_id,
            "property_type": unit.property_type,
            "start_date": history.start_date,
            "end_date": history.end_date,
        }
        for unit, history in rows
    ]


def get_owner_history(
    db: Session,
    owner_id: str,
) -> list[dict] | None:
    if db.get(Owner, owner_id) is None:
        return None

    rows = db.execute(
        select(OwnershipHistory)
        .where(
            OwnershipHistory.owner_id == owner_id
        )
        .order_by(
            OwnershipHistory.start_date.desc().nullslast()
        )
    ).scalars().all()

    return [
        {
            "history_id": row.ownership_history_id,
            "unit_id": row.unit_id,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "source_order_id": row.source_order_id,
        }
        for row in rows
    ]