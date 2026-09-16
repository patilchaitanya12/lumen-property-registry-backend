from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"],
)


@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size

    total = db.scalar(
        select(func.count()).select_from(Order)
    ) or 0

    items = db.scalars(
        select(Order)
        .order_by(Order.transaction_date.desc().nullslast())
        .offset(offset)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "order_id": order.order_id,
                "source_regis": order.source_regis,
                "unit_id": order.unit_id,
                "location_id": order.location_id,
                "procedure_name": order.procedure_name,
                "procedure_value": order.procedure_value,
                "transaction_date": (
                    order.transaction_date.isoformat()
                    if order.transaction_date
                    else None
                ),
            }
            for order in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return {
        "order_id": order.order_id,
        "source_regis": order.source_regis,
        "unit_id": order.unit_id,
        "location_id": order.location_id,
        "procedure_name": order.procedure_name,
        "procedure_value": order.procedure_value,
        "transaction_date": (
            order.transaction_date.isoformat()
            if order.transaction_date
            else None
        ),
    }
