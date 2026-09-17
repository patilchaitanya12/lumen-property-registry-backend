from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import history_service

router = APIRouter(
    prefix="/api/history",
    tags=["History"],
)


@router.get("")
def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return history_service.list_history(
        db=db,
        page=page,
        page_size=page_size,
    )