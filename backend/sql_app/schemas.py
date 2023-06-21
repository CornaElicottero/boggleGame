from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class PlayerCreate(BaseModel):
    name: str
    email: str
    password: str


class PlayerRead(BaseModel):
    email: str
    password: str
    salt: str

    class Config:
        orm_mode = True


class Error(BaseModel):
    message: str


class PlayerUpdate(BaseModel):
    name: str
    password: str
    salt: str
    matches: int
    wins: int
    email: str
