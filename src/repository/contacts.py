import datetime as DT
from sqlalchemy import select, update, func, extract, and_
from datetime import date, timedelta
# from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.asyncio import AsyncSession


from src.models.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

    
async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first n results
    :param db: AsyncSession: Pass a database connection to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts in the database.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the offset of the first row to return
    :param db: AsyncSession: Pass in the database session to use
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function is used to retrieve a contact from the database.
        It takes in two arguments:
            1) The id of the contact you want to retrieve. This is an integer value, and it's required.
            2) The user who owns this contact (the one who created it). This is a User object, and it's required.
    
    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contact by user
    :return: A contact object, or none if it doesn't exist
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()

async def get_contacts_by_name(contact_name: str, db: AsyncSession, user: User):
    """
    The get_contacts_by_name function takes in a contact name and returns all contacts with that name.
        
    :param contact_name: str: Specify the name of the contact to be searched for
    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts that match the given name
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).where(Contact.name.ilike(contact_name))
    # stmt = select(Contact).filter_by(name = contact_name)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contacts_by_surname(contact_surname: str, db: AsyncSession, user: User):
    """
    The get_contacts_by_surname function returns a list of contacts with the given surname.
        
    :param contact_surname: str: Filter the contacts by surname
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Filter the contacts by user
    :return: All contacts with the given surname
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).where(Contact.surname.ilike(contact_surname))
    # stmt = select(Contact).filter_by(surname = contact_surname)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact_by_email(contact_email: str, db: AsyncSession, user: User):
    """
    The get_contact_by_email function takes in a contact_email and a user, and returns the contact with that email.
    If no such contact exists, it returns None.
    
    :param contact_email: str: Filter the database for a contact with that email
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure the user is only getting their own contacts
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(email = contact_email, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()

async def get_contact_by_birthday(birthday: date, n:int, db: AsyncSession, user: User):
    # today = date.today()
    """
    The get_contact_by_birthday function returns a list of contacts whose birthday is within n days from the given date.
        Args:
            birthday (date): The date to compare against.
            n (int): The number of days after the given date to search for birthdays in.
    
    :param birthday: date: Filter the contacts by their birthday
    :param n:int: Determine how many days after the birthday to search for
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure that the user is only getting contacts from their own list
    :return: A list of contacts whose birthday is between the date passed as parameter and n days later
    :doc-author: Trelent
    """
    n_days_later = birthday+ timedelta(days=n)
    stmt = select(Contact).filter_by(user=user).where(and_(Contact.birthday != None, Contact.b_date.between(birthday, n_days_later)))
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user id from the token
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user = user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactUpdateSchema): A ContactUpdateSchema object containing all fields that can be updated for a given user's contacts.  
            This is validated by pydantic before being passed into this function, so we don't need to worry about it here.
    
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactUpdateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the request
    :return: The updated contact
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user = user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        # stmt = (update(Contact).filter_by(id=contact_id)).values(name = body.name, 
        #                                                          surname = body.surname,
        #                                                          email = body.email,
        #                                                          birthday = body.birthday,
        #                                                          phone = body.phone,
        #                                                          nfo = body.info,
        #                                                          created_at = func.now())
        # print(stmt)
        # result = await db.execute(stmt)
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.birthday = body.birthday
        contact.phone = body.phone
        contact.info = body.info
        contact.created_at = func.now()
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.
        
    :param contact_id: int: Identify which contact to delete
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure that the user is deleting their own contact and not someone else's
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user = user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact