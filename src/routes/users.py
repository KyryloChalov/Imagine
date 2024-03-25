import pickle
import uuid

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, Query, status, UploadFile, File, Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.models import User, Role
from src.schemas.user import UserChangeRoleResponse, UserChangeRole, UserResponse, AboutUser, UserUpdateSchema
from src.services.auth import auth_service
from src.conf import messages
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
    "/", response_model=list[UserResponse], dependencies=[Depends(access_to_route_all)]
)
async def get_all_users(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
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


@router.patch("/{id}", response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_user(body: UserUpdateSchema, id: uuid.UUID = Path(), db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    """
    The update_user function updates a user in the database. Can do it only current User or Admin
        Args:
            body (UserUpdateSchema): The updated user information.
            id (uuid.UUID): The unique identifier of the user to update.
            db (AsyncSession): An async session for interacting with the database.
                Defaults to Depends(get_db).
        Returns:
            User: A User object representing an updated version of the original 
    
    :param body: UserUpdateSchema: Validate the data that is passed to the function
    :param id: uuid.UUID: Get the user id from the url
    :param db: AsyncSession: Pass the database connection to the repository
    :param user: User: Get the current user
    :return: An updated user object
    
    """
    email = user.email
    if user.id != id and user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)
    try:
        user = await repositories_users.update_user(id, body, db, user)
        print(user.email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
        # якщо змінився email то забираємо з кэшу і записуємо новий юзер
        if email != user.email:
            _ = auth_service.cache.unlink(email)
        auth_service.cache.set(user.email, pickle.dumps(user))
        auth_service.cache.expire(user.email, 300)
    except:
        raise HTTPException(status_code=409, detail=messages.USER_OR_EMAIL_NOT_UNIQUE)
    return user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: uuid.UUID = Path(), 
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):   
    """
    The delete_user function deletes a user from the database.
        The function takes in an id as a path parameter and returns a message indicating that the user has been deleted.
        If no user is found with the given id, then it will return an HTTP 404 error code with detail message of &quot;User not found&quot;. 
    
    
    :param id: uuid.UUID: Get the user id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the token
    :return: A dict with a message
    :doc-author: Trelent
    """
    user = await repositories_users.delete_user(id, db, user)
    print(user.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    if user.username == messages.USER_NOT_HAVE_PERMISSIONS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.USER_NOT_HAVE_PERMISSIONS)
    user_hash = str(user.email)
    _ = auth_service.cache.unlink(user_hash)
    return {"message": messages.USER_DELETED}


@router.patch("/change_role/{user_id}", response_model=UserChangeRoleResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20)), Depends(access_to_route_all)])
async def change_user_role(body: UserChangeRole, user_id: uuid.UUID = Path(), db: AsyncSession = Depends(get_db), 
                           user: User = Depends(auth_service.get_current_user)):
    # changed_role = RoleAccess([Role.user, Role.moderator])
    print(body.role)
    print(Role.moderator)
    if body.role == Role.user or body.role == Role.moderator:
        user = await repositories_users.change_user_role(user_id, body, db, user)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
        auth_service.cache.set(user.email, pickle.dumps(user))
        auth_service.cache.expire(user.email, 300)
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=messages.WRONG_ROLE)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
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
async def get_username_info(
    username: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    user, num_photos = await repositories_users.get_info_by_username(username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    user.num_photos = num_photos
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_avatar_url(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
    public_id = f"photos/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
