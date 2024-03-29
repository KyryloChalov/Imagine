import datetime as DT
from typing import List
import uuid
import qrcode
import cloudinary
import cloudinary.uploader
from src.conf.config import config
from src.conf.constants import ALLOWED_CROP_MODES
from src.conf.messages import PHOTO_NOT_FOUND

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


def init_cloudinary():
    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )


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


async def get_QR_code(path: str, unique_photo_id: uuid, db: AsyncSession) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(path)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_code_file = "my_qr_code.png"
    img.save(qr_code_file)

    init_cloudinary()
    upload_result = cloudinary.uploader.upload(
        qr_code_file,
        public_id=f"Qr_Code/{unique_photo_id}",
        overwrite=True,
        invalidate=True,
    )
    return upload_result["secure_url"]


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
    init_cloudinary()

    unique_photo_id = uuid.uuid4()
    public_photo_id = f"Photos_of_user/{user.username}/{unique_photo_id}"
    try:
        r = cloudinary.uploader.upload(
            photofile.file, public_id=public_photo_id, overwrite=True
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Wrong file type (need a picture)!")

    src_url = r["url"]

    check_tags_quantity(list_tags)
    tags = await assembling_tags(list_tags, db)

    # QR_code = await get_QR_code(src_url, unique_photo_id, db)
    id = user.id
    new_photo = Photo(
        path=src_url,
        description=description,
        path_transform=None,
        user_id=id,
        tags=tags,
        public_photo_id=public_photo_id,
    )

    try:
        db.add(new_photo)
        await db.commit()
        await db.refresh(new_photo)
    except Exception as e:
        await db.rollback()
        raise e
    return {"success message": PHOTO_SUCCESSFULLY_ADDED}

async def add_tag_to_photo(photo_id: int, name_tag: str, db: AsyncSession):
    """
    The add_tag_to_photo function adds a tag to the photo.
        Args:
            photo_id (int): The id of the photo.
            name_tag (str): The name of the tag.
        Returns:
            dict: A dictionary with success message if everything went well, or an error message otherwise.
    
    :param photo_id: int: Specify the photo to which you want to add a tag
    :param name_tag: str: Specify the name of the tag to be added
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary
    :doc-author: Trelent
    """
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

    """
    The get_all_photos function returns a list of Photo objects.
    
    :param skip_photos: int: Skip the first n photos
    :param photos_per_page: int: Specify the number of photos to be returned per page
    :param db: AsyncSession: Pass in the database connection
    :return: A list of photo objects
    """
    result = await db.execute(
        select(Photo).order_by(Photo.id).offset(skip_photos).limit(photos_per_page)
    )

    photos = result.scalars().all()

    return photos


async def get_photo_by_id(photo_id: int, db: AsyncSession) -> dict | None:

    """
    The get_photo_by_id function returns a photo object from the database.
        Args:
            photo_id (int): The id of the photo to be returned.
            db (AsyncSession): An async session for querying the database.
    
    :param photo_id: int: Specify the id of the photo we want to retrieve
    :param db: AsyncSession: Pass in the database connection to the function
    :return: A dictionary with the photo's information
    :doc-author: Trelent
    """
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    photo = result.scalar_one_or_none()

    return photo


async def delete_photo(photo_id: int, user: User, db: AsyncSession) -> bool:

    """
    The delete_photo function deletes a photo from the database and cloudinary.
        Args:
            photo_id (int): The id of the photo to be deleted.
            user (User): The user who is deleting the photo.
            db (AsyncSession): An async session for interacting with the database.
        Returns:
            bool: True if successful, False otherwise.
    
    :param photo_id: int: Specify the photo to be deleted
    :param user: User: Check if the user is authorized to delete a photo
    :param db: AsyncSession: Pass the database session to the function
    :return: True if the photo was deleted and false if not
    """
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    photo = result.scalar_one_or_none()

    if not photo:
        return False

#<<<<<<< oleksandr
#    if user.role == Role.admin or user.role == Role.moderator or photo.user_id == user.id:
#        cloudinary.config(
#        cloud_name=config.CLOUDINARY_NAME,
#        api_key=config.CLOUDINARY_API_KEY,
#        api_secret=config.CLOUDINARY_API_SECRET,
#        secure=True,
#    )
#=======
#<<<<<<< transform
    if (
        user.role == Role.admin
        or user.role == Role.moderator
        or photo.user_id == user.id
    ):
        init_cloudinary()
# =======
# <<<<<<< oleksandr
#    if user.role == Role.admin or photo.user_id == user.id:
#        cloudinary.config(
#        cloud_name=config.CLOUDINARY_NAME,
#        api_key=config.CLOUDINARY_API_KEY,
#        api_secret=config.CLOUDINARY_API_SECRET,
#        secure=True,
#    )
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
# >>>>>>> dev
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
    """
    The del_photo_tag function deletes a tag from the photo.
        Args:
            photo_id (int): The id of the photo to delete a tag from.
            name_tag (str): The name of the tag to be deleted.
        Returns:
            dict: A dictionary containing success message if successful, or an error message otherwise.
    
    :param photo_id: int: Find the photo in the database
    :param name_tag: str: Specify the name of the tag to be deleted
    :param db: AsyncSession: Pass the database connection to the function
    :return: A dictionary
    """
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



async def change_photo(
    user: User,
    photo_id: int,
    db: AsyncSession,
    width: int,
    height: int,
    crop_mode: str,
    effect: str,
) -> Photo:

    if crop_mode in ALLOWED_CROP_MODES:
        transformation = [
            {"width": width, "height": height},
            {"crop": crop_mode},
            {"effect": effect},
        ]
    else:
        raise HTTPException(status_code=400, detail="This crop mode is not allowed!")

    query = select(Photo).filter(Photo.id == photo_id)
    result = await db.execute(query)
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=400, detail=PHOTO_NOT_FOUND)

    # завантажуємо файл на клаудинарі з трансформацією
    init_cloudinary()

    unique_photo_id = uuid.uuid4()
    public_photo_id = f"Photos_of_user/{user.username}/{unique_photo_id}"
    r = cloudinary.uploader.upload(
        photo.path,
        public_id=public_photo_id,
        overwrite=True,
        transformation=transformation,
    )

    url = cloudinary.CloudinaryImage(public_photo_id).build_url()
    photo.path_transform = url
    QR_code = await get_QR_code(url, unique_photo_id, db)

    try:
        # db.add(new_photo)
        await db.commit()
        await db.refresh(photo)
    except Exception as e:
        await db.rollback()
        raise e

    return {"transformed_url": url, "QR code": QR_code}


async def make_avatar_from_photo(
    user: User,
    photo_id: int,
    effect_mode: str,
    db: AsyncSession,
) -> Photo:

    query = select(Photo).filter(Photo.id == photo_id)
    result = await db.execute(query)
    photo = result.scalar_one_or_none()

    avatar = [
        {"gravity": "face", "height": 200, "width": 200, "crop": "thumb"},
        {"radius": "max"},
        {"effect": effect_mode},
        {"focus": "auto"},
        {"b_auto": "predominant_contrast"},
        {"fetch_format": "auto"},
    ]
    if not photo:
        raise HTTPException(status_code=400, detail=PHOTO_NOT_FOUND)

    init_cloudinary()

    unique_photo_id = uuid.uuid4()
    public_photo_id = f"Photos_of_user/{user.username}/{unique_photo_id}"
    r = cloudinary.uploader.upload(
        photo.path,
        public_id=public_photo_id,
        overwrite=True,
        transformation=avatar,
    )

    # забрати посилання но нове фото, покласти його у photo.path_transform та зберігти дані у базі
    # url = cloudinary.CloudinaryImage(photo.public_photo_id).build_url(
    #     transformation=avatar
    # )
    url = cloudinary.CloudinaryImage(public_photo_id).build_url()
    QR_code = await get_QR_code(url, unique_photo_id, db)

    return {"avatar": url, "QR code": QR_code}

  

async def search_photos(search_keyword: str, photos_per_page: int, skip_photos: int,
                    db: AsyncSession, user: User) -> list[Photo]:
    """
    The search_photos function searches for photos that match the search_keyword.
        The function returns a list of Photo objects that match the search_keyword.
        
    
    :param search_keyword: str: Search for photos that contain the keyword in their description or tags
    :param photos_per_page: int: Limit the number of photos per page
    :param skip_photos: int: Skip the number of photos specified by this parameter
    :param db: AsyncSession: Create a connection to the database
    :param user: User: Check if the user is logged in or not
    :return: A list of photos
    """
    stmt = select(Photo).where(or_(Photo.description.ilike(f"%{search_keyword}%"),
                            and_(
                    Tag.name == search_keyword,
                    # mtm
                    Photo.id == photo_m2m_tag.c.photo_id,
                    Tag.id == photo_m2m_tag.c.tag_id,
                                )
                            )).group_by(Photo.id).order_by(
        Photo.id).offset(skip_photos).limit(photos_per_page)
    result = await db.execute(stmt)
    photos_key_word = result.scalars().all()
    return photos_key_word


# может у кого то получится об'единить 2 запроса в один и вибрать со средним рейтингом
# вмксто функции search_photos_by_filter где ми находим 2-мя запросами
# async def search_photo(search_keyword: str, rate_min: float, rate_max: float, photos_per_page: int, skip_photos: int,
#                     db: AsyncSession, user: User) -> list[Photo]:
    
#     if rate_min or rate_max:
#         rate_min = rate_min or 0.01
#         rate_max = rate_max or 5.0
#     stmt = (select(Photo)
#                 .join(photo_m2m_tag)
#                 .join(Tag)
#                 .join(Rating)
#                 .where(or_(Photo.description.ilike(f"%{search_keyword}%"),
#                            and_(
#                             Tag.name == search_keyword,
#                             Photo.id == photo_m2m_tag.c.photo_id,
#                             Tag.id == photo_m2m_tag.c.tag_id,
#                                 )
#                            ))
#                 .group_by(Photo.id)
#                 .having(and_(
#             func.avg(Rating.rating) >= rate_min,
#             func.avg(Rating.rating) <= rate_max
#         ))
#                 .order_by(Photo.id)
#                 .offset(skip_photos)
#                 .limit(photos_per_page)
#                 )
#     print(stmt)
#     result = await db.execute(stmt)
#     photos_with_filter = result.scalars().all()
#     return photos_with_filter

async def search_photos_by_filter(search_keyword: str, rate_min: float, rate_max: float, photos_per_page: int, skip_photos: int,
                    db: AsyncSession, user: User) -> list[Photo]:
    # ищем по ключевому слову в Description Photo со средним рейтингом в диапазоне
    """
    The search_photos_by_filter function searches for photos by a search keyword,
        and filters the results with average rating in range from minimum to maximum rating.
        
    
    :param search_keyword: str: Search for a keyword in the description of the photo
    :param rate_min: float: Specify the minimum rating of a photo
    :param rate_max: float: Specify the minimum rating of a photo
    :param photos_per_page: int: Specify the number of photos to be displayed on one page
    :param skip_photos: int: Skip the first n photos
    :param db: AsyncSession: Access the database
    :return: A list of photo objects
    """
    if rate_min or rate_max:
        rate_min = rate_min or 0.1
        rate_max = rate_max or 5.0
        print(rate_min, rate_max)
    stmt = (select(Photo)
                .join(Rating)
                .where(Photo.description.ilike(f"%{search_keyword}%"))
                .group_by(Photo.id)
                .having(and_(
            func.avg(Rating.rating) >= rate_min,
            func.avg(Rating.rating) <= rate_max
        ))
                .order_by(Photo.id)
                .offset(skip_photos)
                .limit(photos_per_page)
                )
    result = await db.execute(stmt)
    photos_key_word = result.scalars().all()
     # ищем по совпадению ключевого слова и Тега со средним рейтингом в диапазоне
    stmt = (select(Photo)
            .join(photo_m2m_tag)
            .join(Tag)
            .join(Rating)
            .where(and_(
        Tag.name == search_keyword,
        Photo.id == photo_m2m_tag.c.photo_id,
        Tag.id == photo_m2m_tag.c.tag_id,
    ))
            .group_by(Photo.id)
            .having(and_(
        func.avg(Rating.rating) >= rate_min,
        func.avg(Rating.rating) < rate_max
    ))
            .order_by(Photo.id)
            .offset(skip_photos)
            .limit(photos_per_page)
            )
    result = await db.execute(stmt)
    photos_by_tags = result.scalars().all()
    # объединяем результаты поиска по ключевому слову и тегу со средним рейтингом в диапазоне и убираем дубликаты из результатов
    photos = photos_key_word + [x for x in photos_by_tags if x not in photos_key_word]
# <<<<<<< oleksandr
#    return photos
# =======
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


# >>>>>>> dev
