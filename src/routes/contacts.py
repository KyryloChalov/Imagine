from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
# from asyncpg.exceptions import UniqueViolationError
from pydantic import ValidationError

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.models.models import User, Role
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/contacts', tags=['contacts'])
search_router = APIRouter(prefix='/search', tags=['search'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[ContactResponse], description='No more than 1 request per 10 seconds',
            dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    # if user.role == Role.admin:
    #     contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    # else:
    """
    The get_contacts function returns a list of contacts.
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify that the limit must be greater than or equal to 10
    :param le: Limit the maximum number of contacts that can be returned
    :param offset: int: Skip the first offset contacts
    :param ge: Specify that the limit must be greater than or equal to 10
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A list of contacts for the current user 
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts

@router.get("/all", response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_all_contacts function returns a list of all contacts.
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value of a parameter
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Specify the offset from which to start retrieving contacts
    :param ge: Specify a minimum value for the parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of all contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    return contacts

@search_router.get("/name", response_model=list[ContactResponse])
async def get_contacts_by_name(name: str = Query(), db: AsyncSession = Depends(get_db), 
                               user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_name function returns a list of contacts that match the name parameter.
    If no contact is found, it will return an empty list.
    
    :param name: str: Specify the name of the contact to be retrieved
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts for the current user
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts_by_name(name, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts

@search_router.get("/surname", response_model=list[ContactResponse])
async def get_contacts_by_surname(surname: str = Query(), 
                                  db: AsyncSession = Depends(get_db), 
                                  user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_surname function returns a list of contacts with the given surname.
    
    :param surname: str: Get the surname of the contact that we want to find
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of contacts with the specified surname for the current user
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts_by_surname(surname, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts

@search_router.get("/email", response_model=ContactResponse)
async def get_contact_by_email(email: str = Query(), 
                               db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_email function is used to retrieve a contact by email.
    The function takes an email as input and returns the contact with that email.
    
    :param email: str: Get the email of the contact to be updated
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact_by_email(email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact

#  получаем список контактов, у которих дні рождения в ближайшие n дней от заданой дати
@search_router.get("/birthday", response_model=list[ContactResponse])
async def get_contacts_by_birthday(birthday: date = Query(date.today()), n: int = 7, 
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_birthday function returns a list of contacts that have birthdays on the given date.
    If no date is provided, it will return contacts with birthdays for the next 7 days.
    
    
    :param birthday: date: Get the contacts with a birthday on that date
    :param n: int: Specify the number of days to look ahead for birthdays
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A list of contacts that have a birthday in the next 7 days
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contact_by_birthday(birthday, n, db, user)
    if contacts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no birthdays for the next 7 days")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by its id.
    
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
            description='No more than 1 request per 10 seconds',
            dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    # cont = await repositories_contacts.get_contact_by_email(body.email, db)
    # if cont is not None:
    #         raise HTTPException(status_code=400, detail="Email not unique")
    """
    The create_contact function creates a new contact in the database.
    It takes as input a ContactSchema object, which is validated against the ContactSchema schema.
    If validation fails, an HTTPException is raised with status_code 400 and details of what went wrong.
    
    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user
    :return: The contact it created
    :doc-author: Trelent
    """
    try:
        contact = await repositories_contacts.create_contact(body, db, user)
    except:
        raise HTTPException(status_code=409, detail="Email not unique")
    return contact

@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), 
                         db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
    It takes an id, and a body containing the updated information for that contact.
    If successful, it returns the updated contact object.
    
    :param body: ContactUpdateSchema: Validate the data sent in the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the user id of the current logged in user
    :return: A contact object
    :doc-author: Trelent
    """
    try:
        contact = await repositories_contacts.update_contact(contact_id, body, db, user)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    except:
        raise HTTPException(status_code=409, detail="Email not unique")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), 
                         db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): A connection to the database.
    
    :param contact_id: int: Specify the contact id to be deleted
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: An object of type contact
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    return contact