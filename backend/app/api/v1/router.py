from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints.warehouses import router as warehouse_router
from app.api.v1.endpoints.locations import router as location_router
from app.api.v1.endpoints.products import cat_router, prod_router
from app.api.v1.endpoints.operations import router as operations_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.ws import router as ws_router

from app.api.v1.endpoints.adjustments import router as adjustments_router
from app.api.v1.endpoints.parties import router as parties_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(warehouse_router)
api_router.include_router(location_router)
api_router.include_router(cat_router)
api_router.include_router(prod_router)
api_router.include_router(operations_router)
api_router.include_router(dashboard_router)
api_router.include_router(ws_router)
api_router.include_router(adjustments_router)
api_router.include_router(parties_router)
