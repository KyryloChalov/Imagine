import datetime as DT
from typing import List
import uuid
from sqlalchemy import select, update, func, extract, and_
from datetime import date, timedelta

# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Photo


async def create_image(
    path: str,
    description: str,
    db: AsyncSession,
):
    """
    The create_image function save data of a new image in cloud storage.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user id from the token
    :return: A contact object
    :doc-author: Trelent
    """
    image = Photo(
        path=path,
        description=description,
        path_tranform=None,
    )
    try:
        db.add(image)
        await db.commit()
        await db.refresh(image)
    except Exception as e:
        return {"error": "Something went wrong!", "Exception": e}
    return {"success mesasge": "Image succefully added!"}
