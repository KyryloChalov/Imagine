from unittest.mock import Mock, patch, AsyncMock

import pytest

from src.services.auth import auth_service


# TODO test get all photos
@pytest.mark.asyncio
def test_get_all_photos():
    pass

# TODO test add photo
def test_add_photo():
    pass


# TODO test get photo by id
def test_get_photo_by_id():
    pass

# TODO test update photo
def test_update_photo():
    pass

# TODO test change photo
def test_change_photo():
    pass

# TODO test delete photo (as admin)
def test_delete_photo_positive():
    pass

# TODO test delete photo (as not owner)
def test_delete_photo_negative():
    pass

# TODO test search photo
def test_search_photo():
    pass

# TODO test filter photo
def test_filter_photo():
    pass

# TODO test rate photo first time
def test_rate_photo_positive():
    pass

# TODO test rate photo again
def test_rate_photo_negative():
    pass

# TODO test get average rating by photo id
def test_get_average_rating_by_photo_id():
    pass

# TODO test get rate of user by photo id
def test_get_rate_of_user_by_photo_id():
    pass

# TODO test delete rate of user by photo id (as admin)
def test_delete_rate_of_user_by_photo_id_admin():
    pass

# TODO test delete rate of user by photo id (as owner of rate)
def test_delete_rate_of_user_by_photo_id_owner():
    pass