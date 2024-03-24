import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/{photo_id}/comments",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def post_comment(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Додати коментар та/або рейтинг 
    (додавати щось одне, або обидва, або нічого)
    201 або помилку
    """
    return user


@router.patch(
    "/{photo_id}/comments/{comment_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def edit_comment(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Редагувати коментар
    (та/або тег?)
    201 або помилку 
    """
    return user


@router.delete(
    "/{photo_id}/comments/{comment_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_comment(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Видалити коментар 
    (додавати щось одне, або обидва, або нічого)
    201 або помилку
    """
    return user
