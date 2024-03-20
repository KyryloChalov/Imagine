from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.models.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user object associated with that email.
    If no such user exists, it returns None.
    
    :param email: str: Specify the email of the user we want to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object, which is a sqlalchemy model
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)
    
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the user's refresh token in the database.
    
    :param user: User: Identify the user in the database,
    :param token: str | None: Update the user's refresh token
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()
    
async def confirmed_email(email: str, db: AsyncSession = Depends(get_db)) -> None:
    """
    The confirmed_email function takes an email address and a database connection as arguments.
    It then uses the get_user_by_email function to retrieve the user with that email address from
    the database. It sets the confirmed field of that user to True, and commits those changes to 
    the database.
    
    :param email: str: Specify the email address of the user to confirm
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    
async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url for a user.
    
    :param email: str: Find the user in the database
    :param url: str | None: Specify that the new url avatar parameter can either be a string or none
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user

async def update_password(user: User, password: str, db: AsyncSession):
    """
    The update_password function takes a user object, a password string, and an async database session.
    It sets the user's password to the new given password and commits it to the database.
    
    :param user: User: Pass in the user object that we want to update
    :param password: str: Set the new password for the user
    :param db: AsyncSession: Pass the database session into the function
    :return: None
    :doc-author: Trelent
    """
    user.password = password
    await db.commit()