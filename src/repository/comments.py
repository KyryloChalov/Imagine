import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, func, extract, and_

from src.database.db import get_db
from src.schemas.comments import CommentSchema, CommentResposeSchema, CommentUpdateSchema
# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.asyncio import AsyncSession

# from src.models.models import Contact, User
from src.models.models import Comment


async def create_comment(comment: CommentSchema,
                         photo_id: int,
                         user_id: uuid.UUID,
                         db: AsyncSession = Depends(get_db)):
    comment = Comment(opinion=comment.opinion,
                      photo_id=photo_id,
                      user_id=user_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comment(comment_id: int,
                      db: AsyncSession = Depends(get_db),
                      ):
    stmt = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(stmt)
    return comment.scalar_one_or_none()


async def get_comment_photo_user_id(photo_id: int,
                                    user_id: uuid.UUID,
                                    db: AsyncSession = Depends(get_db),
                                    ):
    stmt = select(Comment).filter_by(photo_id=photo_id, user_id=user_id)
    comment = await db.execute(stmt)
    return comment.scalars().all()


async def get_comment_photo_id(photo_id: int,
                               db: AsyncSession = Depends(get_db), ):
    stmt = select(Comment).filter_by(photo_id=photo_id)
    comment = await db.execute(stmt)
    return comment.scalars().all()


async def edit_comment(comment_id: int,
                       body: CommentUpdateSchema,
                       db: AsyncSession = Depends(get_db), ):
    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        return None

    if comment.opinion is not None:
        comment.opinion = body.opinion

    try:

        await db.commit()
        await db.refresh(comment)
    except:
        raise HTTPException(status_code=500, detail="Error updating comment")

    return comment


async def delete_comment(comment_id: int,
                         db: AsyncSession = Depends(get_db),
                         ):
    stmt = select(Comment).filter_by(id=comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment
