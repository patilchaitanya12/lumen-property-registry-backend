from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Location, Unit

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"],
)


@router.get("")
def list_locations(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Location)

    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Location.location_id.ilike(pattern),
                Location.community.ilike(pattern),
                Location.building_name.ilike(pattern),
            )
        )

    total = db.scalar(
        select(func.count()).select_from(
            stmt.order_by(None).subquery()
        )
    ) or 0

    locations = db.scalars(
        stmt
        .order_by(Location.community, Location.building_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "location_id": location.location_id,
                "community": location.community,
                "building_name": location.building_name,
                "project": location.project,
            }
            for location in locations
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{location_id}")
def get_location(
    location_id: str,
    db: Session = Depends(get_db),
):
    location = db.get(Location, location_id)

    if location is None:
        raise HTTPException(
            status_code=404,
            detail="Location not found",
        )

    unit_count = db.scalar(
        select(func.count())
        .select_from(Unit)
        .where(Unit.location_id == location_id)
    ) or 0

    return {
        "location_id": location.location_id,
        "area_name": location.area_name,
        "community": location.community,
        "project": location.project,
        "project_land": location.project_land,
        "building_no": location.building_no,
        "building_name": location.building_name,
        "unit_count": unit_count,
    }