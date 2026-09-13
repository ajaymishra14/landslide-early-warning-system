from fastapi import APIRouter
from app.api.routes import health, locations, predictions, alerts, environmental, analysis, settings

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(locations.router)
api_router.include_router(predictions.router)
api_router.include_router(alerts.router)
api_router.include_router(environmental.router)
api_router.include_router(analysis.router)
api_router.include_router(settings.router)

from app.api.routes import operations
api_router.include_router(operations.router)

from app.api.routes import whatsapp
api_router.include_router(whatsapp.router)

from app.api.routes import roads, satellite
api_router.include_router(roads.router)
api_router.include_router(satellite.router)
