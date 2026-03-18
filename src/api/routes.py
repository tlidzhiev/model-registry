from fastapi import APIRouter

from .models import router as model_router
from .versions import router as versions_router

router = APIRouter()
router.include_router(model_router, prefix="/models")
router.include_router(versions_router, prefix="/models")
