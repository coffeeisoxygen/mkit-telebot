"""router untuk user crud operation."""

from fastapi import APIRouter, Depends, status

from app.deps.dep_manager import get_user_service
from app.schemas import UserCreate, UserPublicResponse
from app.services.users.srv_user_crud import UserCrudService

router = APIRouter()


@router.post(
    "",
    response_model=UserPublicResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in: UserCreate,
    service: UserCrudService = Depends(get_user_service),
) -> UserPublicResponse:
    return await service.create_user(user_in)
