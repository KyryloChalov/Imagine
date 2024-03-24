import pickle
import time
from typing import Annotated

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.models.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users
from src.repository import photos as repositories_photos


router = APIRouter(prefix="/photos", tags=["photos"])
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
async def get_all_photos(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Отримати всі світлини
    Пагінований список
    """
    return user


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="No more than 1 request per 20 second",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
)
async def put_photo(
    photo_description: str = None,
    file: UploadFile = File(),
    tags: list = [],
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Додати світлину
    201 або помилку
    """

    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"{user.id}/{int(time.time())}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"{user.id}/{int(time.time())}")
    print(src_url)
    add_photo = await repositories_photos.create_photo(
        src_url,
        photo_description,
        db,
    )
    return add_photo


@router.get(
    "/{photo_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_photo(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Отримати світлину за id
    Світлина з даними (опис, коментарі, лінл та QR-код)
    """
    return user


@router.delete(
    "/{photo_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def del_photo(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Видалити світлину
    201 або помилку
    """
    return user


@router.put(
    "/{photo_id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def edit_photo_record(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Редагувати опис/додати теги
    201 або помилку
    """
    return user


@router.post(
    "/{photo_id}/changes/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def change_photo(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Змінити світлину
    round, high, width, face, cartoonify, vignette, borders
    Можна одразу повертати json з лінком та QR-кодом на світлину - так і треба
    """
    return user


@router.post(
    "/{photo_id}/rating/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def put_rating(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Поставити рейтинг
    """
    return user


@router.delete(
    "/{photo_id}/rating/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_rating(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Видалити рейтинг
    """
    return user


@router.get(
    "/search/",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_photo(user: User = Depends(auth_service.get_current_user)):
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
async def filter_photo(user: User = Depends(auth_service.get_current_user)):
    ...
    """
    потребує пояснення - Юрій?
    Сортування Фільтрація результатів пошуку
    "rating=BIG|SMALL,  date=NEW|OLD для адмінів+  {user_id}"
    Пагінований список або помилку
    """
    return user
