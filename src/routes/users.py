import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users


router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_me(user: User = Depends(auth_service.get_current_user)):
    """
    The get_me function returns the current user's information.
        get:
            summary: Get the current user's information.
            description: Returns a UserResponse object containing all of the current user's info, including their username and email address.  This endpoint is protected by JWT authentication, so you must provide a valid token in order to access it.
    
    :param user: User: Specify the type of data that will be returned
    :return: The current user
    :doc-author: Trelent
    """
    return user


@router.patch("/avatar", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar_url(file: UploadFile = File(), 
                            user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The update_avatar_url function takes a file and user as input,
        uploads the file to cloudinary, updates the avatar_url in the database
        and returns a UserResponse object.
    
    :param file: UploadFile: Upload the file to cloudinary
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: The user object with the updated avatar_url
    :doc-author: Trelent
    """
    public_id = f"HW13/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user