from fastapi import Depends
from libgravatar import Gravatar

# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.models.models import User
from src.schemas.user import UserSchema
from src.services.auth import auth_service
from typing import List


def create_users(count: int, db: AsyncSession = Depends(get_db)):

    print("============= create_users 1 ===========")
    number_user = 5
    # number_user = len(db.query(User).all()) + 1
    print(f"{number_user = }")

    for num in range(number_user, (number_user + count)):
        body = UserSchema(
            name="Fake_user",
            username=f"user_{str(num)}",
            email=f"user_{str(num)}@gmail.com",
            password="123456",
        )
        body.password = auth_service.get_password_hash(body.password)

        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        new_user = User(**body.model_dump(), avatar=avatar, confirmed=True)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)


def seed_users(count_users: int = 3):
    print("============= seed_users 1 ===========")
    create_users(count_users, db=get_db)


def main():
    seed_users()


if __name__ == "__main__":
    main()
