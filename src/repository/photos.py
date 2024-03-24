import datetime as DT
from typing import List
import uuid
from sqlalchemy import select, update, func, extract, and_
from datetime import date, timedelta

# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import SOMETHING_WRONG, PHOTO_SUCCESSFULLY_ADDED
from src.models.models import Photo


async def create_photo(
    path: str,
    description: str,
    db: AsyncSession,
):
    """
    The create_photo function save data of a new photo in cloud storage.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user id from the token
    :return: A contact object
    :doc-author: Trelent
    """
    photo = Photo(
        path=path,
        description=description,
        path_transform=None,
    )
    try:
        db.add(photo)
        await db.commit()
        await db.refresh(photo)
    except Exception as e:
        return {"error": SOMETHING_WRONG, "Exception": e}
    return {"success message": PHOTO_SUCCESSFULLY_ADDED}
