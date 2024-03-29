import pickle
import time
from typing import Annotated, List


from fastapi import APIRouter, HTTPException, Depends, Query, status, UploadFile, File, Form

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.schemas.photos import PhotosResponse
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
# <<<<<<< oleksandr
    ...
# =======

# >>>>>>> dev
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


#<<<<<<< transform
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
#=======
#@router.post("/tags/{photo_id}")
#>>>>>>> dev
async def add_tag(
    photo_id: int,
    tag: str,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The add_tag function adds a tag to the photo with the given id.
        If there is no such tag, it will be created.
        If there is already such a tag under this photo, an error message will be displayed.
    
    :param photo_id: int: Identify the photo to which we want to add a tag
    :param tag: str: Specify the tag that will be added to the photo
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :param : Get the photo id
    :return: A tag, which is added to the photo
    """
    tag = await repositories_photos.add_tag_to_photo(photo_id, tag, db)
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
    
    """
    The delete_tag function deletes a tag of the photo_id from the database.
        Args:
            photo_id (int): The id of the photo to delete a tag from.
            tag (str): The name of the tag to be deleted.
        Returns:
            dict: A dictionary containing information about whether or not 
                deleting was successful and if it wasn't, why it failed.
    
    :param photo_id: int: Identify the photo to delete a tag from
    :param tag: str: Specify the tag to be deleted
    :param user: User: Get the current user from the auth_service
    :param db: AsyncSession: Pass the database connection to the function
    :return: A tag object
    :doc-author: Trelent
    """
    tag = await repositories_photos.del_photo_tag(photo_id, tag, db)
    return tag


@router.get(
    "/search/",
    response_model=list[PhotosResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_photo(photos_per_page: int = Query(10, ge=10, le=500),
                    skip_photos: int = Query(0, ge=0),
                    search_keyword: str = Query(),
                    rate_min: float = Query(None, ge=0, le=5),
                    rate_max: float = Query(None, ge=0, le=5),
                    user: User = Depends(auth_service.get_current_user),
                    db: AsyncSession = Depends(get_db)):
    ...
    """
    Пошук по тегу, слову, користувачу
    "tag, word для адмінів + {user_id}"
    Пагінований список або помилку
    """
    if rate_min is None and rate_max is None:
        photos = await repositories_photos.search_photos(search_keyword, photos_per_page, skip_photos, db, user)
    else:
        photos = await repositories_photos.search_photos_by_filter(search_keyword, rate_min, rate_max,
                                                         photos_per_page, skip_photos, 
                                                         db, user)
    if photos == []:
        raise  HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Photo with the specified search parameters was not found")
    return photos