import pickle
import time
from typing import Annotated, List


from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.models.models import User, Photo, CropMode, EffectMode, Effect
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users
from src.repository import photos as repositories_photos
from src.conf.messages import NO_PHOTO_BY_ID, PHOTO_SUCCESSFULLY_DELETED
from src.routes.ratings import access_delete


router = APIRouter(prefix="/photos", tags=["photos"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
async def get_all_photos(
    skip_photos: int = 0,
    photos_per_page: int = 10,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...
    """
    Отримати всі світлини
    Пагінований список
    """
    all_photos = await repositories_photos.get_all_photos(
        skip_photos, photos_per_page, db
    )
    return all_photos


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="No more than 1 request per 20 second",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
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
    name="get_photo",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    ...
    """
    Отримати світлину за id
    Світлина з даними (опис, коментарі, лінк та QR-код)
    """
    photo = await repositories_photos.get_photo_by_id(photo_id, db)

    if photo:
        return photo

    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_BY_ID)


@router.delete(
    "/{photo_id}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def del_photo(
    photo_id: int,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Видалити світлину
    201 або помилку
    """

    result = await repositories_photos.delete_photo(photo_id, user, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID
        )

    return {"message": PHOTO_SUCCESSFULLY_DELETED}


@router.patch(
    "/{photo_id}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def edit_photo_record(
    photo_id: int,
    new_description: str,
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
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def change_photo(
    photo_id: int,
    width: int | None,
    height: int | None,
    crop_mode: CropMode = Form(
        None, description="The cropping mode: fill, thumb, fit, limit, pad, scale"
    ),
    effect: Effect = Form(None, description="The art effects"),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Змінити світлину
    round, high, width, face, cartoonify, vignette, borders
    Можна одразу повертати json з лінком та QR-кодом на світлину - так і треба
    """
    if crop_mode is not None:
        crop_mode = crop_mode.name
    else:
        crop_mode = None
    if effect is not None:
        effect = effect.value
    else:
        effect = None

    url_QR = await repositories_photos.change_photo(
        user,
        photo_id,
        db,
        width,
        height,
        crop_mode,
        effect,
    )

    return url_QR


@router.post(
    "/{photo_id}/avatar/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def make_avatar(
    photo_id: int,
    effect_mode: EffectMode = Form(
        None, description="The cropping mode: fill, thumb, fit, limit, pad, scale"
    ),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Робимо з фото аватар
    """

    if effect_mode is not None:
        effect_mode = effect_mode.name
    else:
        effect_mode = None

    url_QR = await repositories_photos.make_avatar_from_photo(
        user,
        photo_id,
        effect_mode,
        db,
    )

    return url_QR


# @router.post(
#     "/{photo_id}/rating/",
#     response_model=UserResponse,
#     dependencies=[Depends(RateLimiter(times=1, seconds=20))],
# )
# async def put_rating(user: User = Depends(auth_service.get_current_user)):
#     ...
#     """
#     Поставити рейтинг
#     """
#     return user


# @router.delete(
#     "/{photo_id}/rating/",
#     response_model=UserResponse,
#     dependencies=[Depends(RateLimiter(times=1, seconds=20))],
# )
# async def delete_rating(user: User = Depends(auth_service.get_current_user)):
#     ...
#     """
#     Видалити рейтинг
#     """
#     return user


# @router.post("/tags/{photo_id}")
# async def add_tag(
#     photo_id: int,
#     tag: str,
#     user: User = Depends(auth_service.get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     tag = await repositories_photos.add_tag_to_photo(photo_id, tag, db)
#     # можна додати теги до світлини за id
#     # якщо тег існує, то додається до списку тегів
#     # якщо тега немає, то додається новий тег
#     # якщо теги закінчились, то додається новий тег
#     return tag


@router.post(
    "/tags/{photo_id}",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def add_tag(
    photo_id: int,
    tag: str,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag = await repositories_photos.add_tag_to_photo(photo_id, tag, db)
    # можна додати теги до світлини за id
    # якщо тег існує, то додається до списку тегів
    # якщо тега немає, то додається новий тег
    # якщо такий тег під світлиною за id вже є - видається повідомлення
    return tag


@router.delete(
    "/tags/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(access_delete)],
)
async def delete_tag(
    photo_id: int,
    tag: str,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # видаляємо тег до світлини за його ім’ям
    # якщо фото нема - видається помилка
    # якщо тега немає, видається сповіщення
    # якщо такий тег під світлиною за id вже є - видається повідомлення
    tag = await repositories_photos.del_photo_tag(photo_id, tag, db)
    return tag


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
