"""register all Router Here."""

from app.api.v1.rtr_user import router as user_router


def setup_router(app):
    app.include_router(user_router, prefix="/api/v1/user", tags=["user"])
