"""скопіював з contacts"""

import re
from typing import Optional
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from src.conf.constants import COMMENT_MIN_LENGTH, COMMENT_MAX_LENGTH


class CommentSchema(BaseModel):
    pass


class CommentResposeSchema(BaseModel):
    pass


class CommentUpdateSchema(BaseModel):
    pass
