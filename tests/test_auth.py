import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

@patch('src.repository.users.get_user_by_email', return_value=None)
@patch('src.repository.users.get_user_by_username', return_value=None)
@patch('src.repository.users.create_user')
@patch('src.routes.auth.auth_service.get_password_hash', return_value='hashed_password')
@patch('src.routes.auth.auth_service.cache.set')
@patch('src.routes.auth.auth_service.cache.expire')
def test_signup_success(
    mock_cache_expire, mock_cache_set, mock_get_password_hash, mock_create_user,
    mock_get_user_by_username, mock_get_user_by_email, client
):
    # Define test data
    user_data = {
        "name": "Test User",
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    }
    expected_response = {"name": "Test User","username": "test_user", "email": "test@example.com"}

    # Mock create_user function
    mock_create_user.return_value = expected_response

    # Send POST request to signup endpoint
    response = client.post("api/auth/signup", json=user_data)

    # Assert response
    assert response.status_code == 201
    assert expected_response in response.json() 

    # Assert that functions were called with expected arguments
    # mock_get_user_by_email.assert_called_once_with('test@example.com', mock_create_user)
    # mock_get_user_by_username.assert_called_once_with('test_user', mock_create_user)
    # mock_get_password_hash.assert_called_once_with('test_password')
    # mock_create_user.assert_called_once_with(user_data, mock_create_user)
    # mock_cache_set.assert_called_once_with('test@example.com', b'{"username": "test_user", "email": "test@example.com"}')
    # mock_cache_expire.assert_called_once_with('test@example.com', 300)

# Additional test cases for error scenarios can be added similarly

