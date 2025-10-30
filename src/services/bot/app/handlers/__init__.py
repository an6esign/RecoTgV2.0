from .start import router as start_router
from .me import router as me_router

__all__ = ["routers"]

routers = [
    start_router,
    me_router,
]