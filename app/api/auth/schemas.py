from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role_id: UUID
    section_id: UUID


class UserUpdate(BaseModel):
    name : Optional[str] = None
    username : Optional[str] = None
    password: Optional[str] = None
    role_id : Optional[UUID] = None
    section_id: Optional[UUID] = None


class RoleforUser(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    username: str
    role : RoleforUser
    section_id: Optional[UUID] = None



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



class FacultyBase(BaseModel):
    employee_id: str
    designation: str
    department_id: int

class FacultyResponse(FacultyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FacultyWithUserResponse(FacultyResponse):
    user: UserResponse

    class Config:
        orm_mode = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class FacultyCreate(FacultyBase):
    user: UserCreate


class FacultyUpdate(BaseModel):
    employee_id: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None

class FacultyResponse(FacultyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FacultyWithUserResponse(FacultyResponse):
    user: UserResponse

    class Config:
        orm_mode = True