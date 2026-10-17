from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):

    username: str

    email: EmailStr

    password: str

    role: Literal["recruiter", "candidate"] = "recruiter"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Literal["recruiter", "candidate"]

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    username: str = Field(min_length=1, max_length=120)


class UserLogin(BaseModel):

    email: EmailStr

    password: str
