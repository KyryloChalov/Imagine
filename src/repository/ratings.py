import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.photos import RatingSchema, RatingResponseSchema
from src.conf import messages
from src.models.models import Comment, Photo


async def create_rating(comment: RatingSchema,
                        photo_id: int,
                        user_id: uuid.UUID,
                        db: AsyncSession = Depends(get_db),
                        ):
    pass


async def get_user_rating_for_photo(photo_id: int,
                                    user_id: uuid.UUID,
                                    db: AsyncSession = Depends(get_db),
                                    ):
    # also used for check if user already set rating for photo
    pass


async def get_avg_rating_for_photo(photo_id: int,
                                   db: AsyncSession = Depends(get_db),
                                   ):
    pass


async def user_already_set_rating_for_photo(photo_id: int,
                                            user_id: uuid.UUID,
                                            db: AsyncSession = Depends(get_db),
                                            ):
    pass
