import uuid
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import List
from sqlalchemy import select, or_, and_, extract
from datetime import datetime

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User, Role, Comment, Rating
from src.schemas.photos import RatingSchema, RatingResponseSchema, RatingAVGResponseSchema

from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config
from src.conf import messages
from src.repository import ratings as repositories_rating

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
                        rating: RatingSchema,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    # repositories_rating.create_rating(db, photo_id, rating, user)

    pass


@router.get(
    "/user/{photo_id}/{user_id}",
    response_model=RatingResponseSchema,
    dependencies=[Depends(access_get)]
)
async def get_user_rating(
        photo_id: int = Path(ge=1),
        user_id: uuid.UUID = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    # repositories_rating.get_user_rating(db, photo_id, user_id)
    pass


@router.get(
    "/{photo_id}",
    response_model=RatingAVGResponseSchema,
    dependencies=[Depends(access_get)],
)
async def get_avg_rating(photo_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    # repositories_rating.get_avg_rating(photo_id, db)
    pass


@router.delete(
    "/{rating_id}",
    # status_code=status.HTTP_204_NO_CONTENT,
    response_model=RatingResponseSchema,
    dependencies=[Depends(access_delete)],
)
async def delete_rating(rating_id: int = Path(ge=1),
                        user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db)):
    pass
