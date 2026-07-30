from fastapi import APIRouter
from .auth import router as auth_router
from .machine import router as machine_router
from .rental import router as rental_router
from .predictions import router as predictions_router
from .events import router as events_router
from .dashboards import router as dashboards_router
from .operators import router as operators_router
from .sites import router as sites_router
from .ws import router as ws_router
from .notifications import router as notifications_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(machine_router, prefix="/machines", tags=["machines"])
api_router.include_router(rental_router, prefix="/rentals", tags=["rentals"])
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
api_router.include_router(dashboards_router)
api_router.include_router(operators_router)
api_router.include_router(sites_router, prefix="/sites", tags=["sites"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ws_router, prefix="/ws", tags=["websocket"])
