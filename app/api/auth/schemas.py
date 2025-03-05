from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role_id: UUID


class UserUpdate(BaseModel):
    name : Optional[str] = None
    username : Optional[str] = None
    password: Optional[str] = None
    role_id : Optional[UUID] = None

class RoleforUser(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    role : RoleforUser

class RoleCreate(BaseModel):
    name: str

class RoleUpdate(BaseModel):
    name : Optional[str]



class RoleResponse(BaseModel):
    name : str
    id: UUID
    created_at : datetime
    updated_at : datetime

class LoginSchema(BaseModel):
    username: str
    password: str
