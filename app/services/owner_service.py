from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Contact, Owner, OwnershipHistory, Unit
from app.schemas.owner import OwnerCreate, OwnerUpdate


def list_owners(
    db: Session,
    query: str | None = None,
    page: int = 1,
    page_size: int = 25,
    include_inactive: bool = False,
) -> dict:
    stmt = select(Owner)

    if not include_inactive:
        stmt = stmt.where(Owner.is_active.is_(True))

    if query:
        pattern = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Owner.owner_id.ilike(pattern),
                Owner.name.ilike(pattern),
                Owner.first_name.ilike(pattern),
                Owner.last_name.ilike(pattern),
                Owner.uae_id_number.ilike(pattern),
                Owner.unified_number.ilike(pattern),
            )
        )

    total = db.scalar(
        select(func.count()).select_from(
            stmt.order_by(None).subquery()
        )
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
                "first_name": owner.first_name,
                "last_name": owner.last_name,
                "owner_type": owner.owner_type,
                "vip_tier": owner.vip_tier,
                "country": owner.country,
                "property_count": owner.property_count,
                "is_active": owner.is_active,
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
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "title": owner.title,
        "owner_type": owner.owner_type,
        "vip_tier": owner.vip_tier,
        "gender": owner.gender,
        "gender_source": owner.gender_source,
        "source_community": owner.source_community,
        "source_file": owner.source_file,
        "country": owner.country,
        "id_number": owner.id_number,
        "uae_id_number": owner.uae_id_number,
        "unified_number": owner.unified_number,
        "passport_expiry_date": owner.passport_expiry_date,
        "birth_date": owner.birth_date,
        "property_count": owner.property_count,
        "calculated_property_count": property_count,
        "communities_owned": owner.communities_owned,
        "community_list": owner.community_list,
        "buildings_list": owner.buildings_list,
        "is_multi_property": owner.is_multi_property,
        "is_portfolio_investor": owner.is_portfolio_investor,
        "has_cross_community": owner.has_cross_community,
        "portfolio_tier": owner.portfolio_tier,
        "has_plot": owner.has_plot,
        "has_apartment": owner.has_apartment,
        "has_villa": owner.has_villa,
        "is_reachable": owner.is_reachable,
        "is_active": owner.is_active,
        "notes": owner.notes,
        "created_at": owner.created_at,
        "updated_at": owner.updated_at,
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


def create_owner(
    db: Session,
    data: OwnerCreate,
) -> Owner:
    owner_id = _generate_owner_id(db, data.name)

    owner = Owner(
        owner_id=owner_id,
        **data.model_dump(),
    )

    db.add(owner)
    db.commit()
    db.refresh(owner)

    return owner


def update_owner(
    db: Session,
    owner_id: str,
    data: OwnerUpdate,
) -> Owner | None:
    owner = db.get(Owner, owner_id)

    if owner is None:
        return None

    values = data.model_dump(exclude_unset=True)

    for field, value in values.items():
        setattr(owner, field, value)

    db.commit()
    db.refresh(owner)

    return owner


def deactivate_owner(
    db: Session,
    owner_id: str,
) -> Owner | None:
    owner = db.get(Owner, owner_id)

    if owner is None:
        return None

    owner.is_active = False

    db.commit()
    db.refresh(owner)

    return owner


def _generate_owner_id(
    db: Session,
    name: str,
) -> str:
    base = (
        name.strip()
        .upper()
        .replace(" ", "-")
        .replace("/", "-")
    )

    base = "".join(
        character
        for character in base
        if character.isalnum() or character == "-"
    )

    base = base[:80] or "OWNER"

    prefix = f"MANUAL-{base}"

    existing = db.scalar(
        select(Owner.owner_id)
        .where(Owner.owner_id.like(f"{prefix}-%"))
        .order_by(Owner.owner_id.desc())
    )

    if existing is None:
        sequence = 1
    else:
        try:
            sequence = int(existing.rsplit("-", 1)[1]) + 1
        except ValueError:
            sequence = 1

    return f"{prefix}-{sequence:04d}"
