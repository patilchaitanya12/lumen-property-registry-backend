from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import unit_service

router = APIRouter(
    prefix="/api/units",
    tags=["Units"],
)


@router.get("")
def list_units(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return unit_service.list_units(
        db=db,
        query=q,
        page=page,
        page_size=page_size,
    )


@router.get("/{unit_id}")
def get_unit(
    unit_id: str,
    db: Session = Depends(get_db),
):
    unit = unit_service.get_unit(
        db=db,
        unit_id=unit_id,
    )

    if unit is None:
        raise HTTPException(
            status_code=404,
            detail="Unit not found",
        )

    return unit


@router.get("/{unit_id}/owners")
def get_unit_owners(
    unit_id: str,
    db: Session = Depends(get_db),
):
    owners = unit_service.get_unit_owners(
        db=db,
        unit_id=unit_id,
    )

    if owners is None:
        raise HTTPException(
            status_code=404,
            detail="Unit not found",
        )

    return {
        "unit_id": unit_id,
        "items": owners,
    }


@router.get("/{unit_id}/history")
def get_unit_history(
    unit_id: str,
    db: Session = Depends(get_db),
):
    history = unit_service.get_unit_history(
        db=db,
        unit_id=unit_id,
    )

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Unit not found",
        )

    return {
        "unit_id": unit_id,
        "items": history,
    }