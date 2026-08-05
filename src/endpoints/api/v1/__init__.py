from fastapi import APIRouter

from . import onboarding

router = APIRouter(tags=["v1"], prefix="/v1")

router.include_router(onboarding.router)