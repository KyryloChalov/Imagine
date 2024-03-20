from datetime import date, datetime
import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import generics

from src.models.models import Contact, Role, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import (
    get_contacts,
    get_all_contacts,
    get_contact,
    get_contacts_by_name,
    get_contacts_by_surname,
    get_contact_by_email,
    get_contact_by_birthday,
    create_contact,
    update_contact,
    delete_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=generics.GUID(), username='test_user', email='test@test.com', password="qwerty", confirmed=True)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit=10, offset=0, db = self.session, user=self.user)
        self.assertEqual(result, contacts)
        
    async def test_get_all_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit=10, offset=0, db = self.session)
        self.assertEqual(result, contacts)
        
    async def test_get_contact(self):
        contact = [Contact(id=1, name='Bill', surname='Gates', email='bill@microsoft.com', phone='911012345678', birthday='1960-03-06', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id=1, db = self.session, user=self.user)
        self.session.execute.assert_called_once()
        self.assertListEqual(result, contact)
        
        
    async def test_get_contacts_by_name(self):
        contacts = [Contact(id=1, name='Bill', surname='Gates', email='bill@microsoft.com', phone='911012345678', birthday='1960-03-06', user_id=self.user),
                    Contact(id=2, name='Steave', surname='Jobs', email='steave@apple.com', phone='901012345678', birthday='1958-03-07', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await get_contacts_by_name(contact_name='Bill', db = self.session, user=self.user)
        self.assertEqual(result, contacts)
        
    async def test_get_contacts_by_surname(self):
        contacts = [Contact(id=1, name='Bill', surname='Gates', email='bill@microsoft.com', phone='911012345678', birthday='1960-03-06', user_id=self.user),
                    Contact(id=2, name='Steave', surname='Jobs', email='steave@apple.com', phone='901012345678', birthday='1958-03-07', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await get_contacts_by_surname(contact_surname='Jobs', db = self.session, user=self.user)
        self.assertEqual(result, contacts)
    
    async def test_get_contact_by_email(self):
        contact = [Contact(id=2, name='Steave', surname='Jobs', email='steave@apple.com', phone='901012345678', birthday='1958-03-07', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_email(contact_email='steave@apple.com', db = self.session, user=self.user)
        self.assertEqual(result, contact)
        
    async def test_get_contact_by_birthday(self):
        contacts = [Contact(id=1, name='Bill', surname='Gates', email='bill@microsoft.com', phone='911012345678', birthday='1960-03-06', user_id=self.user),
                    Contact(id=2, name='Steave', surname='Jobs', email='steave@apple.com', phone='901012345678', birthday='1958-03-07', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_birthday(birthday=date.today(), n=7, db = self.session, user=self.user)
        self.assertEqual(result, contacts)
        
    async def test_get_contact_by_email_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await get_contact_by_email(contact_email='steave@apple.com', db = self.session, user=self.user)
        self.assertIsNone(result)
    
    async def test_create_contact(self):
        body = ContactSchema(name="Bill", surname="Gates", email="bill@microsoft.com", phone="911012345678", birthday="1960-03-06")
        contact = [Contact(name='Bill', surname='Gates', email='bill@microsoft.com', phone='911012345678', birthday='1960-03-06', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await create_contact(body=body, db = self.session, user = self.user)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)    
        
    async def test_update_contact(self):
        body = ContactUpdateSchema(name="Bill", surname="Gates", email="bill@microsoft.com", phone="911012345678", birthday="1962-03-06", info = "some info", created_at=datetime.now())
        mocked_contact = MagicMock() 
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name='Bill', surname='Gates', email='bill@microsoft.com', phone='911012345678', birthday='1960-03-06', info = "some info", created_at=datetime.now(), user_id=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(contact_id=1, body=body, db = self.session, user=self.user)
        self.session.execute.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday) 
        
    async def test_delete_contact(self):
        contact = [Contact(id=2, name='Steave', surname='Jobs', email='steave@apple.com', phone='901012345678', birthday='1958-03-07', user_id=self.user)]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id=1, db = self.session, user = self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result, contact)



if __name__ == '__main__':
    unittest.main()

