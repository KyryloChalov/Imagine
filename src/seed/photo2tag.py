from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.models import Photo, Tag, Base, Table  # photo_m2m_Tag
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


async def seed_photo_2_tag(db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових тегів до photo (за замовченням: count: int = 30)
    """
    result = await db.execute(select(Photo))
    photos = result.scalars().all()

    photos_id = []
    for photo in photos:
        photos_id.append(photo.id)
    print(f"{photos_id = }")

    result = await db.execute(select(Tag))
    tags = result.scalars().all()
    tags_id = []
    for tag in tags:
        tags_id.append(tag.id)
    print(f"{tags_id = }")

    # for _ in range(len(photos_id)):
    #     for i in range(random.randint(1, 5)):
    #         ...
    #         new_photo2tag = Table(
    #             "photo_m2m_tag",
    #             Base.metadata,
    #             photo_id=photos_id[random.randint(0, len(photos_id) - 1)],
    #             tag_id=tags_id[random.randint(0, len(tags_id) - 1)],
    #         )

    # ph_id = photos_id[random.randint(0, len(photos_id) - 1)]
    # tg_id = tags_id[random.randint(0, len(tags_id) - 1)]

    # new_photo2tag = Photo_m2m_Tag(photo_id=ph_id, tag_id=tg_id)

    # print(f" === >>> {new_photo2tag = } <<< ===")

    # db.add(new_photo2tag)
    # await db.commit()
    # await db.refresh(new_photo2tag)
