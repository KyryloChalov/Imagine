from unittest.mock import Mock, patch, AsyncMock

import pytest
from sqlalchemy import select

from src.services.auth import auth_service
from src.models.models import User, Role
from src.services.roles import RoleAccess
from src.routes.contacts import access_to_route_all
from tests.conftest import TestingSessionLocal, test_user

  

def test_get_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0
        
def test_get_all_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("contacts/all", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0


def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/contacts", headers=headers, json={
            "name": "test",
            "surname": "test",
            "email": "gates@microsoft.com",
            "phone": "380504444567",
            "birthday": "2022-03-08",
            'info': 'test'
        })
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "test"
        assert data["surname"] == "test"
        assert data["email"] == "gates@microsoft.com"
        assert data["phone"] == "380504444567"
        assert data["birthday"] == "2022-03-08"
        
@pytest.mark.asyncio    
async def test_get_all_contacts_not_allowed(client, get_token, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == test_user.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.role = Role.user
            await session.commit()
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("contacts/all", headers=headers)
        assert response.status_code == 403, response.text
        data = response.json()
        assert data["detail"] == "FORBIDDEN"