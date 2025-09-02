"""register all Router Here."""

from app.api.v1.rtr_user import router as user_router
from app.api.v1.rtr_admin import router as admin_router


def setup_router(app):
    app.include_router(user_router, prefix="/api/v1/user", tags=["user"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
