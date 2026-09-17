from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Order


def list_orders(
    db: Session,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    offset = (page - 1) * page_size

    total = db.scalar(
        select(func.count()).select_from(Order)
    ) or 0

    orders = db.scalars(
        select(Order)
        .order_by(
            Order.transaction_date.desc().nullslast()
        )
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
                "transaction_date": order.transaction_date,
            }
            for order in orders
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def get_order(
    db: Session,
    order_id: str,
) -> dict | None:
    order = db.get(Order, order_id)

    if order is None:
        return None

    return {
        "order_id": order.order_id,
        "source_regis": order.source_regis,
        "unit_id": order.unit_id,
        "location_id": order.location_id,
        "procedure_name": order.procedure_name,
        "procedure_value": order.procedure_value,
        "transaction_date": order.transaction_date,
    }