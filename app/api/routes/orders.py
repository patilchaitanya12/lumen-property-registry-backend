from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import order_service

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"],
)


@router.get("")
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return order_service.list_orders(
        db=db,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = order_service.get_order(
        db=db,
        order_id=order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order