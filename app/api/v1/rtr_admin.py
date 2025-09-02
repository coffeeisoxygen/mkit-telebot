"""router untuk admin operation."""

from fastapi import APIRouter, Depends, status

from app.deps.dep_manager import get_auth_service
from app.schemas.sch_user import UserLogin
from app.services.auth.srv_auth import AuthService

router = APIRouter()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def admin_login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(login_data)
    if not user.is_superuser:
        return {"error": "Not an admin"}
    # TODO: Integrasi session, token, dsb
    return {"message": "Admin login success", "user_id": user.id}
