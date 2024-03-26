from faker import Faker
from fastapi import Depends
from pprint import pprint
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from src.conf.constants import TAGS_MAX_NUMBER
from src.database.db import get_db
from src.models.models import Photo, Tag, Base

import random

fake_data: Faker = Faker(["uk_UA", "en_US"])


class Photo2Tag(Base):
    __tablename__ = "photo_m2m_tag"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)


async def seed_photo_2_tag(db: AsyncSession = Depends(get_db)):
    """
    генерація таблиці many_2_many
    """
    print("photo2tags")
    result = await db.execute(select(Photo))
    photos = result.scalars().all()

    photos_id = []
    for photo in photos:
        photos_id.append(photo.id)
    photos_id = list(set(photos_id))
    # print(f"*********** {photos_id = }")
    # print(f"{len(photos_id) = }")

    result = await db.execute(select(Tag))
    tags = result.scalars().all()
    tags_id = []
    for tag in tags:
        tags_id.append(tag.id)
    tags_id = list(set(tags_id))
    # print(f"{tags_id = }")
    # print(f"{len(tags_id) = }")

    pairs: list = []
    count = len(photos_id) * len(tags_id) // 2
    # print(f"+++++++++++ {count = }")
    for n in range(count):
        pair = {}
        photo_id = photos_id[random.randint(0, len(photos_id) - 1)]
        tag_id = tags_id[random.randint(0, len(tags_id) - 1)]
        pair = {"photo_id": photo_id, "tag_id": tag_id}
        # print(f"{n+1}.. {pair = }")
        skip = False
        count_tags = 1

        for i in range(0, len(pairs)):
            if int(photo_id) == int(pairs[i]["photo_id"]) and int(tag_id) == int(
                pairs[i]["tag_id"]
            ):
                # print(">>>", photo_id, ":", tag_id, "==", pairs[i])
                # print({">>> identical <<<"})
                skip = True
                # print("break ident")
                break

            if int(photo_id) == int(pairs[i]["photo_id"]):
                count_tags += 1
                # print(">>> ------------------ ", photo_id, " :        ", tag_id, f"{count_tags = }")
                # print(f"{count_tags = }")
                if count_tags > TAGS_MAX_NUMBER:
                #     print("---", pairs[i])
                #     print({">>> over <<<"})
                    skip = True
                    # print("break over")
                    break

        # if (count_tags <= 3) or (not skip):
        # print(f"                                          {count_tags = },    {skip = }")
        if not skip:
            pairs.append(pair)
        # pairs.append(pair)

        new_photo2tag = Photo2Tag(photo_id=photo_id, tag_id=tag_id)

        db.add(new_photo2tag)
        await db.commit()
        await db.refresh(new_photo2tag)
    # print(" ========= ")
    # print(f"{len(pairs) = }")
    # pprint(pairs)
