import pickle
import time
from typing import Annotated


from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form

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
from src.conf.messages import NO_PHOTO_BY_ID


router = APIRouter(prefix="/photos", tags=["photos"])


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
    photo_description: str | None = Form(
        None, description="Add a description to your photo (string)"
    ),
    file: UploadFile = File(),
    tags: list[str] = Form(
        None, description="Tags to associate with the photo (list of strings)"
    ),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Додати світлину
    201 або помилку
    """
    list_tags = tags[0].split(",")

    new_photo = await repositories_photos.create_photo(
        file,
        photo_description,
        user,
        db,
        list_tags,
    )
    return new_photo


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


@router.patch(
    "/{photo_id}",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
)
async def edit_photo_record(
    photo_id: int,
    new_description: str,
    tags: list[str] = Form(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...
    """
    Редагувати опис/додати теги
    201 або помилку
    """
    tags = tags[0].split(",")
    updated_photo = await repositories_photos.edit_photo_description(
        user, photo_id, new_description, tags, db
    )

    if updated_photo:
        return updated_photo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID)


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
