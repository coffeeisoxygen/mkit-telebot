"""register all Router Here."""

from app.api.v1 import rtr_user


def setup_router(app):
    app.include_router(rtr_user, prefix="/api/v1/user", tags=["user"])
