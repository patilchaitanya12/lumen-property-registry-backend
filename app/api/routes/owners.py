from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.owner import OwnerCreate, OwnerResponse, OwnerUpdate
from app.services import owner_service

router = APIRouter(prefix="/api/owners", tags=["Owners"])


@router.get("")
def list_owners(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return owner_service.list_owners(
        db=db,
        query=q,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )


@router.post(
    "",
    response_model=OwnerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_owner(
    data: OwnerCreate,
    db: Session = Depends(get_db),
):
    try:
        return owner_service.create_owner(
            db=db,
            data=data,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/{owner_id}")
def get_owner(
    owner_id: str,
    db: Session = Depends(get_db),
):
    owner = owner_service.get_owner(
        db=db,
        owner_id=owner_id,
    )

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return owner


@router.patch(
    "/{owner_id}",
    response_model=OwnerResponse,
)
def update_owner(
    owner_id: str,
    data: OwnerUpdate,
    db: Session = Depends(get_db),
):
    try:
        owner = owner_service.update_owner(
            db=db,
            owner_id=owner_id,
            data=data,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return owner


@router.delete(
    "/{owner_id}",
    response_model=OwnerResponse,
)
def delete_owner(
    owner_id: str,
    db: Session = Depends(get_db),
):
    owner = owner_service.deactivate_owner(
        db=db,
        owner_id=owner_id,
    )

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return owner


@router.get("/{owner_id}/units")
def get_owner_units(
    owner_id: str,
    db: Session = Depends(get_db),
):
    units = owner_service.get_owner_units(
        db=db,
        owner_id=owner_id,
    )

    if units is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return {
        "owner_id": owner_id,
        "items": units,
        "total": len(units),
    }


@router.get("/{owner_id}/history")
def get_owner_history(
    owner_id: str,
    db: Session = Depends(get_db),
):
    history = owner_service.get_owner_history(
        db=db,
        owner_id=owner_id,
    )

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return {
        "owner_id": owner_id,
        "items": history,
        "total": len(history),
    }

@router.get("/{owner_id}/360")
def get_owner_360(
    owner_id: str,
    db: Session = Depends(get_db),
):
    owner = owner_service.get_owner_360(
        db=db,
        owner_id=owner_id,
    )

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    return owner