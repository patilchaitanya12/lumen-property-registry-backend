from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Location, Unit


def list_locations(
    db: Session,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    offset = (page - 1) * page_size

    total = db.scalar(
        select(func.count()).select_from(Location)
    ) or 0

    locations = db.scalars(
        select(Location)
        .order_by(
            Location.community,
            Location.building_name,
        )
        .offset(offset)
        .limit(page_size)
    ).all()

    location_ids = [
        location.location_id
        for location in locations
    ]

    unit_counts: dict[str, int] = {}

    if location_ids:
        count_rows = db.execute(
            select(
                Unit.location_id,
                func.count(Unit.unit_id),
            )
            .where(
                Unit.location_id.in_(location_ids)
            )
            .group_by(Unit.location_id)
        ).all()

        unit_counts = {
            location_id: count
            for location_id, count in count_rows
            if location_id is not None
        }

    return {
        "items": [
            {
                "location_id": location.location_id,
                "area_name": location.area_name,
                "community": location.community,
                "project": location.project,
                "project_land": location.project_land,
                "building_no": location.building_no,
                "building_name": location.building_name,
                "unit_count": unit_counts.get(
                    location.location_id,
                    0,
                ),
            }
            for location in locations
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def get_location(
    db: Session,
    location_id: str,
) -> dict | None:
    location = db.get(Location, location_id)

    if location is None:
        return None

    units = db.scalars(
        select(Unit)
        .where(Unit.location_id == location_id)
        .order_by(
            Unit.unit_code,
            Unit.unit_number,
            Unit.unit_id,
        )
    ).all()

    return {
        "location_id": location.location_id,
        "area_name": location.area_name,
        "community": location.community,
        "project": location.project,
        "project_land": location.project_land,
        "building_no": location.building_no,
        "building_name": location.building_name,
        "unit_count": len(units),
        "units": [
            {
                "unit_id": unit.unit_id,
                "property_id": unit.property_id,
                "unit_code": unit.unit_code,
                "unit_number": unit.unit_number,
                "property_type": unit.property_type,
            }
            for unit in units
        ],
    }
