from aiogram import Router

from .admin import router as admin_router
from .common import router as common_router
from .user import router as user_router


def setup_routers() -> Router:
    router = Router()
    router.include_router(common_router)
    router.include_router(admin_router)
    router.include_router(user_router)
    return router
