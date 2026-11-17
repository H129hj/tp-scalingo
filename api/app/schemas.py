from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""


class NoteOut(NoteIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
