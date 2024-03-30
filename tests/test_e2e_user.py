from unittest.mock import Mock, patch, AsyncMock

import pytest

from src.services.auth import auth_service


def test_get_me(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("users/me", headers=headers)
        assert response.status_code == 200, response.text

# #TODO test update avatar
# def test_update_avatar():
#     pass

# #TODO test get all users
# def test_get_all_users(client, get_token, monkeypatch):
#     pass

# #TODO test update user
# def test_update_user():
#     pass

# #TODO test change user role
# def test_change_user_role():
#     pass

# #TODO test get some user info
# def test_get_some_user_info():
#     pass

# #TODO test delete user
# def test_delete_user():
#     pass

