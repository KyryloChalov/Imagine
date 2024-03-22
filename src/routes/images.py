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


router = APIRouter(prefix="/images", tags=["images"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_all_images(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Отримати всі світлини
    Пагінований список
    """
    return user


@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def put_image(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Додати світлину
    201 або помилку
    """
    return user

@router.get(
    "/{image_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_image(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Отримати світлину за id
    Світлина з даними (опис, коментарі, лінл та QR-код)
    """
    return user


@router.delete(
    "/{image_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def del_image(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Видалити світлину
    201 або помилку
    """
    return user


@router.put(
    "/{image_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def edit_image_record(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Редагувати опис/додати теги
    201 або помилку
    """
    return user


@router.post(
    "/{image_id}/changes/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def change_image(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Змінити світлину
    round, high, width, face, cartoonify, vignette, borders
    Можна одразу повертати json з лінком та QR-кодом на світлину - так і треба
    """
    return user


@router.get(
    "/search/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_image(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Пошук по тегу, слову, користувачу
    "tag, word для адмінів + {user_id}"
    Пагінований список або помилку
    """
    return user

    # потребує пояснення - Юрій?
@router.get(
    "/search/filter",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def filter_image(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    потребує пояснення - Юрій?
    Сортування Фільтрація результатів пошуку
    "rating=BIG|SMALL,  date=NEW|OLD для адмінів+  {user_id}"
    Пагінований список або помилку
    """
    return user
