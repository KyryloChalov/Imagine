from pathlib import Path

import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, 
                          password=config.REDIS_PASSWORD, encoding="utf-8",
                          decode_responses=True)
    delay = await FastAPILimiter.init(r)
    yield delay


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(contacts.router)
app.include_router(contacts.search_router)
app.include_router(auth.auth_router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Your contacts here"}

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If it doesn't, then we know something is wrong with our connection to the database.
    
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary with a message key and value
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Database 'contacts' is healthy"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")