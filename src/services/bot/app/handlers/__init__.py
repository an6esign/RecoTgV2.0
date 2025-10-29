from .start import router as start_router
from .contact import router as contact_router
from .me import router as me_router

__all__ = ["routers"]

routers = [
    start_router,
    contact_router,
    me_router,
]