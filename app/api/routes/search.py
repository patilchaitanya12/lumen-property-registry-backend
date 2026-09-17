from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import search_service

router = APIRouter(
    prefix="/api/search",
    tags=["Search"],
)


@router.get("")
def search(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
):
    return search_service.search_registry(
        db=db,
        query=q,
    )