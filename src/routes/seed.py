from fastapi import APIRouter
from src.seed.users import seed_users

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/users")
async def seed_fake_users(number_users: int = 3):
    seed_users(number_users)
    return {"message": f"You have {number_users} new fake Users"}


# @router.post("/contacts")
# async def seed_fake_contacts(number_contacts: int = 10):
#     seed_contacts(number_contacts)
#     return {"message": f"You have {number_contacts} new fake Contacts"}
