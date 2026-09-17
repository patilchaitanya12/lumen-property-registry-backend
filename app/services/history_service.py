from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Owner, OwnershipHistory, Unit


def list_history(
    db: Session,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    offset = (page - 1) * page_size

    total = db.scalar(
        select(func.count()).select_from(OwnershipHistory)
    ) or 0

    rows = db.execute(
        select(
            OwnershipHistory,
            Unit.unit_code,
            Owner.name,
        )
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
        .offset(offset)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "history_id": history.ownership_history_id,
                "unit_id": history.unit_id,
                "unit_code": unit_code,
                "owner_id": history.owner_id,
                "owner_name": owner_name,
                "start_date": history.start_date,
                "end_date": history.end_date,
                "source_order_id": history.source_order_id,
                "created_at": history.created_at,
            }
            for history, unit_code, owner_name in rows
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }