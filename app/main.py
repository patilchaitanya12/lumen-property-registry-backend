from fastapi import FastAPI

from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.history import router as history_router
from app.api.routes.locations import router as locations_router
from app.api.routes.owners import router as owners_router
from app.api.routes.search import router as search_router
from app.api.routes.units import router as units_router

app = FastAPI(
    title="Lumen Property Registry API",
    version="0.1.0",
)

app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(owners_router)
app.include_router(units_router)
app.include_router(locations_router)
app.include_router(history_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "lumen-property-registry-backend",
    }