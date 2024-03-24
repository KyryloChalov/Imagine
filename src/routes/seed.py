from fastapi import APIRouter, Depends
from src.seed.users import seed_users, seed_basic_users
from src.seed.tags import seed_tags
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/basic_users")
async def seed_fake_basic_users(db: AsyncSession = Depends(get_db)):
    await seed_basic_users(db)
    return {
        "message": "You have 5 new fake users: admin, moderator, user, guest, banned"
    }


@router.post("/fake_users")
async def seed_fake_users(number_users: int = 3, db: AsyncSession = Depends(get_db)):
    await seed_users(number_users, db)
    return {"message": f"You have {number_users} new fake Users"}


@router.post("/fake_tags")
async def seed_fake_tags(number_tags: int = 10, db: AsyncSession = Depends(get_db)):
    await seed_tags(number_tags, db)
    return {"message": f"You have {number_tags} new fake Tags"}
