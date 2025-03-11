from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    id: str  # MongoDB ObjectID as string

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    token: str
    token_type: str