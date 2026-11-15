from fastapi import APIRouter

from app.api.gauges.handler import router as gauges_router
from app.api.invoices.handler import router as invoices_router
from app.api.ping.handler import router as ping_router
from app.api.readings.handler import router as readings_router
from app.api.realty.handler import router as realty_router
from app.api.tariffs.handler import router as tariffs_router
from app.api.users.handler import router as users_router

router = APIRouter()
router.include_router(ping_router)
router.include_router(users_router)
router.include_router(realty_router)
router.include_router(readings_router)
router.include_router(invoices_router)
router.include_router(tariffs_router)
router.include_router(gauges_router)
