from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import location_service

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"],
)


@router.get("")
def list_locations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return location_service.list_locations(
        db=db,
        page=page,
        page_size=page_size,
    )


@router.get("/{location_id}")
def get_location(
    location_id: str,
    db: Session = Depends(get_db),
):
    location = location_service.get_location(
        db=db,
        location_id=location_id,
    )

    if location is None:
        raise HTTPException(
            status_code=404,
            detail="Location not found",
        )

    return location