import datetime as DT
from typing import List
import uuid
import cloudinary
import cloudinary.uploader
from src.conf.config import config

from src.models.models import User, Tag
from sqlalchemy import select, update, func, extract, and_
from datetime import date, timedelta
from fastapi import File

# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import SOMETHING_WRONG, PHOTO_SUCCESSFULLY_ADDED
from src.models.models import Photo


async def get_or_create_tag(tag_name: str, db: AsyncSession) -> Tag:

    existing_tag = await db.execute(select(Tag).filter(Tag.name == tag_name))
    tag = existing_tag.scalar_one_or_none()

    # If the tag does not exist, create a new one
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)

    return tag


async def create_photo(
    photofile: File(),
    description: str | None,
    user: User,
    db: AsyncSession,
    list_tags: List[str],
):
    """
    The create_photo function save data of a new photo in cloud storage.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user id from the token
    :return: A contact object
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )

    unique_photo_id = uuid.uuid4()
    public_photo_id = f"Photos_of_user/{user.username}/{unique_photo_id}"
    r = cloudinary.uploader.upload(
        photofile.file, public_id=public_photo_id, overwrite=True
    )

    print(r)

    src_url = r["url"]

    print(r["public_id"])
    print(r["url"])
    input()
    # photo_url = r["secure_url"]
    # public_id = r["public_id"]

    tags = []
    for tag_name in tags:
        existing_tag = await get_or_create_tag(tag_name, db)
        tags.append(existing_tag)

    new_photo = Photo(
        path=src_url,
        description=description,
        path_transform=None,
        user_id=user.id,
        tags=tags,
    )
    try:
        db.add(new_photo)
        await db.commit()
        await db.refresh(new_photo)
    except Exception as e:
        await db.rollback()
        raise e
    return {"success message": PHOTO_SUCCESSFULLY_ADDED}
