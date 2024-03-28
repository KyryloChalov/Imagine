import datetime as DT
from typing import List
import uuid
import cloudinary
import cloudinary.uploader
from src.conf.config import config

from src.models.models import Rating, Role, User, Tag, photo_m2m_tag
from sqlalchemy import or_, select, update, func, extract, and_, delete
from datetime import date, timedelta
from fastapi import File, HTTPException

# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import (
    SOMETHING_WRONG,
    PHOTO_SUCCESSFULLY_ADDED,
    TAG_SUCCESSFULLY_ADDED,
)
from src.models.models import Photo


async def get_or_create_tag(tag_name: str, db: AsyncSession) -> Tag:

    existing_tag = await db.execute(select(Tag).filter(Tag.name == tag_name))
    tag = existing_tag.scalar_one_or_none()

    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        # await db.commit()
        # await db.refresh(tag)

    return tag


def check_tags_quantity(tags: list[str]) -> bool | None:
    if len(tags) > 5:
        raise HTTPException(
            status_code=400, detail="You can add no more 5 tags to one photo."
        )
    return True


async def assembling_tags(source_tags: list[str], db: AsyncSession) -> List[Tag]:
    tags = []

    for tag_name in source_tags:
        existing_tag = await get_or_create_tag(tag_name, db)
        tags.append(existing_tag)

    return tags


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

    src_url = r["url"]

    check_tags_quantity(list_tags)
    tags = await assembling_tags(list_tags, db)

    id = user.id
    new_photo = Photo(
        path=src_url,
        description=description,
        path_transform=None,
        user_id=id,
        tags=tags,
        public_photo_id=public_photo_id,
        created_at=DT.datetime.now(),
    )

    try:
        db.add(new_photo)
        await db.commit()
        await db.refresh(new_photo)
    except Exception as e:
        await db.rollback()
        raise e
    return {"success message": PHOTO_SUCCESSFULLY_ADDED}



# async def add_tag_to_photo(photo_id: int, name_tag: str, db: AsyncSession):
#     stmt = select(Photo).filter_by(id=photo_id)
#     result = await db.execute(stmt)
#     photo = result.scalar_one_or_none()
#     print(photo)
#     print(photo_id)
#     # Если фото нет, вернем ошибку
#     if photo is None:
#         raise HTTPException(status_code=404, detail="Photo not found")
#     # Определим существование тега
#     stmt = select(Tag).filter_by(name=name_tag)
#     result = await db.execute(stmt)
#     tag = result.scalar_one_or_none()
#     # Если тега нет, создадим его
#     if tag is None:
#         tag = Tag(name=name_tag)
#         db.add(tag)
#         # Используем flush, чтобы получить id тега, коториий будет добавлена
#         await db.flush()
#     # Добавляем связь
#     db.execute(photo_m2m_tag.insert(), params={"photo_id": photo.id, "tag_id": tag.id})
#     await db.commit()
#     return {"success message": TAG_SUCCESSFULLY_ADDED}



async def add_tag_to_photo(photo_id: int, name_tag: str, db: AsyncSession):
    stmt = select(Photo).filter_by(id=photo_id)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    # Определим колічество тегов под фото
    stmt = (
        select(func.count())
        .select_from(Photo)
        .where(
            and_(
                Photo.id == photo_id,
                # mtm
                Photo.id == photo_m2m_tag.c.photo_id,
            )
        )
    )
    num_tags: int = await db.execute(stmt)
    num_tags = num_tags.scalar()
    if num_tags >= 5:
        raise HTTPException(
            status_code=400, detail="You can add no more 5 tags to one photo."
        )
    # Определим существование тега
    stmt = select(Tag).filter_by(name=name_tag)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    # Если тега нет, создадим его
    if tag is None:
        tag = Tag(name=name_tag)
        db.add(tag)
        # Используем flush, чтобы получить id тега, коториий будет добавлен
        await db.flush()
    else:
        # Определим есть ли у єтого фото такой тег
        stmt = (
            select(func.count())
            .select_from(Photo)
            .where(
                and_(
                    Photo.id == photo_id,
                    # mtm
                    Photo.id == photo_m2m_tag.c.photo_id,
                    Tag.id == photo_m2m_tag.c.tag_id,
                )
            )
        )
        num_tags: int = await db.execute(stmt)
        num_tags = num_tags.scalar_one_or_none()
        if num_tags:
            raise HTTPException(status_code=400, detail="This photo has had this tag!")
    # Добавляем связь
    stmt = photo_m2m_tag.insert().values(photo_id=photo.id, tag_id=tag.id)
    await db.execute(stmt)
    await db.commit()
    return {"success message": TAG_SUCCESSFULLY_ADDED}


async def edit_photo_description(
    user: User, photo_id: int, description: str, db: AsyncSession
) -> dict:

    query_result = await db.execute(
        select(Photo).where(Photo.user_id == user.id).where(Photo.id == photo_id)
    )
    photo = query_result.scalar()

    # Перевіряємо отриманий список тегів на кількість (<=5)
    # check_tags_quantity(list_tags)
    # await assembling_tags(list_tags, db)  # Додаємо відсутні теги у базу
    # tags_from_base = await db.execute(select(Tag).filter(Tag.name.in_(list_tags)))

    # tags = []
    # for tag in tags_from_base:
    #     tags.append(tag)

    if photo:
        photo.description = description

        # photo.tags = tags  # Тут чомусь виникає помилка

        try:
            await db.commit()
            await db.refresh(photo)
            return photo
        except Exception as e:
            await db.rollback()
            raise e


async def get_all_photos(
    skip_photos: int, photos_per_page: int, db: AsyncSession
) -> list[Photo]:

    result = await db.execute(
        select(Photo).order_by(Photo.id).offset(skip_photos).limit(photos_per_page)
    )

    photos = result.scalars().all()

    return photos


async def get_photo_by_id(photo_id: int, db: AsyncSession) -> dict | None:

    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    photo = result.scalar_one_or_none()

    return photo


async def delete_photo(photo_id: int, user: User, db: AsyncSession) -> bool:

    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    photo = result.scalar_one_or_none()

    if not photo:
        return False

# <<<<<<< oleksandr
    if user.role == Role.admin or photo.user_id == user.id:
        cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )
# =======
#    if (
#        user.role == Role.admin
#        or user.role == Role.moderator
#        or photo.user_id == user.id
#    ):
#        cloudinary.config(
#            cloud_name=config.CLOUDINARY_NAME,
#            api_key=config.CLOUDINARY_API_KEY,
#            api_secret=config.CLOUDINARY_API_SECRET,
#            secure=True,
#        )
# >>>>>>> dev
        cloudinary.uploader.destroy(photo.public_photo_id)
        try:
            # Видалення пов'язаних рейтингів
            await db.execute(
                Rating.__table__.delete().where(Rating.photo_id == photo_id)
            )
            # Deleting linked photo
            await db.delete(photo)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise e


async def del_photo_tag(photo_id: int, name_tag: str, db: AsyncSession):
    stmt = select(Photo).filter_by(id=photo_id)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    # Определим существование тега
    stmt = select(Tag).filter_by(name=name_tag)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    # Если тега нет, сообщаем ошибку
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    # Определим есть ли у єтого фото такой тег
    stmt = select(Photo).where(
        and_(
            Photo.id == photo_id,
            # mtm
            Photo.id == photo_m2m_tag.c.photo_id,
            tag.id == photo_m2m_tag.c.tag_id,
        )
    )
    photo_tag = await db.execute(stmt)
    photo_tag = photo_tag.scalar_one_or_none()
    if not photo_tag:
        raise HTTPException(status_code=400, detail="This photo don't has this tag!")
    # удаляем связь из m2m
    stmt = delete(photo_m2m_tag).where(
        photo_m2m_tag.c.photo_id == photo_id, photo_m2m_tag.c.tag_id == tag.id
    )
    await db.execute(stmt)
    await db.commit()
    return {"success message": "Tag successfully deleted"}
  

async def search_photo(search_keyword: str, photos_per_page: int, skip_photos: int,
                    db: AsyncSession, user: User) -> list[Photo]:
    print("photo")
    stmt = select(Tag).filter_by(name=search_keyword)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    # Если тега нет, ищем только по Description
    stmt = select(Photo).where(Photo.description.ilike(f"%{search_keyword}%")).order_by(
        Photo.id).offset(skip_photos).limit(photos_per_page)
    result = await db.execute(stmt)
    photos_key_word = result.scalars().all()
    if tag is None:
        print("tag is none")
        return photos_key_word
    # ищем и по Description
    stmt = select(Photo).where(and_(
                    Tag.name == search_keyword,
                    # mtm
                    Photo.id == photo_m2m_tag.c.photo_id,
                    Tag.id == photo_m2m_tag.c.tag_id,
            )).order_by(Photo.id).offset(skip_photos).limit(photos_per_page)
    
    result = await db.execute(stmt)
    photos_by_tags = result.scalars().all()
    photos = photos_key_word + [x for x in photos_by_tags if x not in photos_key_word]
    if photos == []:
        raise  HTTPException(status_code=400, detail=f"Photo with keyword={search_keyword} not found")
    return photos

async def search_photos(search_keyword: str, rate_min: float, rate_max: float, photos_per_page: int, skip_photos: int,
                    db: AsyncSession, user: User) -> list[Photo]:
    # Фільтр не работает - падает сервер
    print("photos")
    stmt = select(Tag).filter_by(name=search_keyword)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    stmt = select(Photo).where(Photo.description.ilike(f"%{search_keyword}%")).order_by(
        Photo.id).offset(skip_photos).limit(photos_per_page)
    result = await db.execute(stmt)
    photos_key_word = result.scalars().all()
    if tag is None:
        print("tag is none")
        return photos_key_word
    print("ищем и по Description")
    if rate_min or rate_max:
        rate_min = rate_min or 0.1
        rate_max = rate_max or 5.0
        print(rate_min, rate_max)
        stmt = select(Photo).where(and_(
                    Tag.name == search_keyword,
                    # mtm
                    Photo.id == photo_m2m_tag.c.photo_id,
                    Tag.id == photo_m2m_tag.c.tag_id,
                    # func.avg(Photo.rating) <= rate_max,
                    # func.avg(Photo.rating) >= rate_min,
                    )).order_by(Photo.id).offset(skip_photos).limit(photos_per_page)
        result = await db.execute(stmt)
        photos_by_tags = result.scalars().all()
    photos = photos_key_word + [x for x in photos_by_tags if x not in photos_key_word]
    if photos == []:
        raise  HTTPException(status_code=400, detail=f"Photo with keyword={search_keyword} not found")
    
#    2-вариант - тоже не рабочий 
    # stmt = select(Tag).filter_by(name=search_keyword)
    # result = await db.execute(stmt)
    # tag = result.scalar_one_or_none()
    # stmt = select(Photo).where(Photo.description.ilike(f"%{search_keyword}%"))
    # print(stmt)
    # if rate_min or rate_max:
    #     rate_min = rate_min or 0.1
    #     rate_max = rate_max or 5.0
    #     print(rate_min, rate_max, Rating.rating)
    #     stmt = select(Photo).filter(and_(func.avg(Photo.rating) >= rate_min, 
    #         func.avg(Photo.rating) <= rate_max)).where(Photo.description.ilike(f"%{search_keyword}%"))
    #     # order_by(Photo.id).offset(skip_photos).limit(photos_per_page) 
    #     print("+++++++++++++++++")
 
    # result = await db.execute(stmt)
    # photos_key_word = result.scalars().all()
    # # Если тега нет, ищем только по Description
    # if tag is None:
    #     print("tag is none")
    #     return photos_key_word
    # # ищем по Description и по тегу
    # stmt = select(Photo).where(and_(
    #                 Tag.name == search_keyword,
    #                 # mtm
    #                 Photo.id == photo_m2m_tag.c.photo_id,
    #                 Tag.id == photo_m2m_tag.c.tag_id,
    #         )).order_by(Photo.id).offset(skip_photos).limit(photos_per_page)
    # result = await db.execute(stmt)
    # photos_by_tags = result.scalars().all()
    # photos = photos_key_word + [x for x in photos_by_tags if x not in photos_key_word]
    # if photos == []:
    #     raise  HTTPException(status_code=400, detail=f"Photo with keyword={search_keyword} not found")
    return photos

