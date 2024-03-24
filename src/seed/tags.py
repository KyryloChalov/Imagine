from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.models import Tag

import random
from faker import Faker

fake_data: Faker = Faker(['uk_UA', 'en_US'])


async def seed_tags(count: int = 10, db: AsyncSession = Depends(get_db)):
    """
    генерація кількох фейкових tags (за замовченням: count_tags: int = 10)
    """
    for _ in range(count):
        name_tag = ""
        name_tag = fake_data.text(random.randint(5, 25))
        print(f"{name_tag = }")

        new_tag = Tag(name=name_tag[:-1])

        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)
