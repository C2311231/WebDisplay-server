from fastapi import APIRouter

from . import v1

router = APIRouter(tags=["api"], prefix="/api")

router.include_router(v1.router)