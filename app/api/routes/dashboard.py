from fastapi import APIRouter

from app.services import dashboard_service

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("")
def dashboard():
    return dashboard_service.get_dashboard_stats()