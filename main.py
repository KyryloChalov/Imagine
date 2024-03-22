from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.conf.config import config
from src.routes import auth, users, images, comments

import redis.asyncio as redis
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        # password=config.REDIS_PASSWORD, # з ним в мене зависає. чи треба тут пароль?
        encoding="utf-8",
        decode_responses=True,
    )
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
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# static_directory = BASE_DIR.joinpath("src").joinpath("static")
static_directory = BASE_DIR.joinpath("templates").joinpath("css")
app.mount("/css", StaticFiles(directory=static_directory), name="css")

image_directory = BASE_DIR.joinpath("templates").joinpath("image")
app.mount("/image", StaticFiles(directory=image_directory), name="image")

app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth.auth_router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(comments.router, prefix="/api")


@app.get("/")
async def read_root(request: Request):
    """
    The greeting message.
    """
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "welcome": f"Welcome!",
            "message": f"This is Imagine from _magic",
            "about_app": "REST API",
        },
    )


# @app.get("/")
# def read_root():
#     return {"message": "Imagine from _magic - буде index.html"}


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
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Database 'contacts' is healthy"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
