from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.models import Photo, User, Comment
from src.conf.constants import (
    COMMENT_MIN_LENGTH,
    COMMENT_MAX_LENGTH,
    PHOTO_PATH_LENGTH,
    TRANSFORM_PATH_LENGTH,
    PHOTO_MIN_DESCRIPTION_LENGTH,
    PHOTO_MAX_DESCRIPTION_LENGTH,
)

import random

fake_data: Faker = Faker(["uk_UA", "en_US"])


async def seed_comments(count: int = 100, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових comments (за замовченням: count: int = 100)
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    users_id = []
    for user in users:
        users_id.append(user.id)
    # print(f"{users_id = }")

    result = await db.execute(select(Photo))
    photos = result.scalars().all()
    photos_id = []
    for photo in photos:
        photos_id.append(photo.id)
    # print(f"{photos_id = }")

    for _ in range(count):
        new_comment = Comment(
            opinion=fake_data.text(
                random.randint(COMMENT_MIN_LENGTH, COMMENT_MAX_LENGTH)
            )[:-1],
            user_id=users_id[random.randint(0, len(users_id) - 1)],
            photo_id=photos_id[random.randint(0, len(photos_id) - 1)],
        )

        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
