import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.conf import messages
from src.models.models import Photo, Rating


async def create_rating(rating: int,
                        photo_id: int,
                        user_id: uuid.UUID,
                        db: AsyncSession = Depends(get_db), ):
    rating = Rating(rating=rating,
                    photo_id=photo_id,
                    user_id=user_id,
                    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_user_rating_for_photo(photo_id: int,
                                    user_id: uuid.UUID,
                                    db: AsyncSession = Depends(get_db),
                                    ):
    # also used for check if user already set rating for photo

    stmt = select(Rating).filter_by(photo_id=photo_id, user_id=user_id)
    rating = await db.execute(stmt)
    return rating.scalar_one_or_none()

async def get_avg_rating(photo_id: int,
                         db: AsyncSession = Depends(get_db),
                         ):
    stmt = select(func.avg(Rating.rating)).filter_by(photo_id=photo_id)
    rating = await db.execute(stmt)
    print(rating)
    return rating.scalar_one_or_none()


async def get_rating(rating_id: int,
                     db: AsyncSession = Depends(get_db),
                     ):
    stmt = select(Rating).filter_by(id=rating_id)
    rating = await db.execute(stmt)
    return rating.scalar_one_or_none()


async def delete_rating(rating_id: int,
                        db: AsyncSession = Depends(get_db),
                        ):
    stmt = select(Rating).filter_by(id=rating_id)
    result = await db.execute(stmt)
    rating = result.scalar_one_or_none()
    if rating:
        await db.delete(rating)
        await db.commit()
    return rating
