import uuid
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List
from sqlalchemy import select, or_, and_, extract, func
from datetime import datetime

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import Photo, User, Role, Rating
from src.schemas.photos import RatingSchema, RatingResponseSchema, RatingAVGResponseSchema

from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config
from src.conf import messages, constants
from src.repository import comments as repositories_comments
from src.repository import ratings as repositories_ratings

router = APIRouter(prefix="/photos/ratings", tags=["photos"])

# Access to the operations by roles
access_get = RoleAccess([Role.admin, Role.moderator, Role.user])
# access_update = RoleAccess([Role.user])
access_create = RoleAccess([Role.user])
access_delete = RoleAccess([Role.admin, Role.moderator])


@router.post(
    "/{photo_id}",
    response_model=RatingResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_create)],
)
async def create_rating(photo_id: int,
                        rate: int = Query(ge=1, le=5),
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user), ):
    print(f'{rate=}')

    photo_exists: Photo | None = await repositories_comments.get_photo_by_id(photo_id, db)

    if photo_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)

    is_rating = await repositories_ratings.get_user_rating_for_photo(photo_id, user.id, db)
    if is_rating:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="You already set rating for this photo",
        )

    new_rating = await repositories_ratings.create_rating(rate, photo_id, user.id, db)
    return new_rating


@router.get(
    "/user/{photo_id}",
    response_model=RatingResponseSchema,
    dependencies=[Depends(access_get)]
)
async def get_user_rating(
        photo_id: int = Path(ge=1),
        user_id: uuid.UUID = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    photo_exists: Photo | None = await repositories_comments.get_photo_by_id(photo_id, db)

    if photo_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)

    if user_id is None:
        user_id = user.id

    rating = await repositories_ratings.get_user_rating_for_photo(photo_id, user_id, db)

    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND)
    return rating


@router.get(
    "/{photo_id}",
    response_model=RatingAVGResponseSchema,
    dependencies=[Depends(access_get)],
)
async def get_avg_rating(photo_id: int = Path(ge=1),
                         user_id: uuid.UUID = None,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    user_id = user.id

    rating = await repositories_ratings.get_user_rating_for_photo(photo_id, user_id, db)
    avg_rating = await repositories_ratings.get_avg_rating(photo_id, db)

    if avg_rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND)

    avg_rating_response = {
        "photo_id": photo_id,
        "rating": round(avg_rating, constants.RATING_DECIMAL_DIGITS)
    }
    return avg_rating_response


@router.delete(
    "/{rating_id}",
    # status_code=status.HTTP_204_NO_CONTENT,
    response_model=RatingResponseSchema,
    dependencies=[Depends(access_delete)],
)
async def delete_rating(rating_id: int = Path(ge=1),
                        user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db)):
    rating = await repositories_ratings.get_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.RATING_NOT_FOUND)

    rating = await repositories_ratings.delete_rating(rating_id, db)
    return rating
