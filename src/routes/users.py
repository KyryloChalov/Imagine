import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, Query, status, UploadFile, File

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User, Role
from src.schemas.user import UserResponse, AboutUser
from src.services.auth import auth_service
from src.conf.config import config
from src.services.roles import RoleAccess
from src.repository import users as repositories_users


router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)

access_to_route_all = RoleAccess([Role.admin, Role.moderator])

@router.get(
    "/", response_model=list[UserResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_users(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):


    """
    The get_all_users function returns a list of all users in the database.
        ---
        get:
            summary: Get all users from the database.  This is an admin or moderator-only function, and will return a 403 error if called by non-admin user.
            description: Returns a list of all users in the database, with optional limit and offset parameters to control pagination (defaults are 10 records per page).  This is an admin-only function, and will return a 403 error if called by non-admin user.  
    
    :param limit: int: Limit the number of users returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of users that can be returned in a single request
    :param offset: int: Offset the number of users returned by the limit: int parameter
    :param ge: Specify a minimum value for the parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of users, and the get_all_users function is decorated with @router
    :doc-author: Trelent
    """
    users = await repositories_users.get_all_users(limit, offset, db)
    return users

@router.patch(
    "/{id}",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_user(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    ...
    """
    Банимо користувача
    banned=TRUE|FALSE
    201 або помилку
    admin
    """
    return user


# @router.post(
#     "/me",
#     response_model=UserResponse,
#     dependencies=[Depends(RateLimiter(times=1, seconds=20))],
# )
# async def edit_me(user: User = Depends(auth_service.get_current_user)):
#     ...
#     """
#     Редагувати свій профіль 
#     201 або помилку
#     """
#     return user


# @router.patch(
#     "/change_role/{user_id}",
#     response_model=UserResponse,
#     dependencies=[Depends(RateLimiter(times=1, seconds=20))],
# )
# async def change_user_role(user: User = Depends(auth_service.get_current_user)):
#     ...
#     """
#     Зміна ролі користувача
#     201 або помилку
#     admin, moderator
#     """
#     return user


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

@router.get("/{username}", response_model=AboutUser)
async def get_username_info(username: str, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    
    user, num_images = await repositories_users.get_info_by_username(username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    user.num_images = num_images
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
    public_id = f"Images/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
