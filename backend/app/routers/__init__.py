from fastapi import APIRouter
from .auth import router as auth_router
from .machine import router as machine_router
from .rental import router as rental_router
from .predictions import router as predictions_router
from .events import router as events_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(machine_router, prefix="/machines", tags=["machines"])
api_router.include_router(rental_router, prefix="/rentals", tags=["rentals"])
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
