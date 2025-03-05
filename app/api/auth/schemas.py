from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role_id: UUID


class UserUpdate(BaseModel):
    name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    role_id : Optional[UUID]

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
