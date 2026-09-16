from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Owner, OwnershipHistory, Unit

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("")
def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(OwnershipHistory, Unit, Owner)
        .join(
            Unit,
            Unit.unit_id == OwnershipHistory.unit_id,
        )
        .join(
            Owner,
            Owner.owner_id == OwnershipHistory.owner_id,
        )
        .order_by(
            OwnershipHistory.created_at.desc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "history_id": history.ownership_history_id,
                "unit_id": unit.unit_id,
                "unit_code": unit.unit_code,
                "owner_id": owner.owner_id,
                "owner_name": owner.name,
                "start_date": history.start_date,
                "end_date": history.end_date,
                "source_order_id": history.source_order_id,
                "created_at": history.created_at,
            }
            for history, unit, owner in rows
        ],
        "page": page,
        "page_size": page_size,
    }