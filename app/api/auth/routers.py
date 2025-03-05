from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.schemas import LoginSchema, RoleResponse, UserCreate, UserResponse, UserUpdate
from app.api.auth.services import RoleService, UserService
from app.core.database import get_session


router = APIRouter(tags=["Auth"], prefix="/auth")


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(db: AsyncSession = Depends(get_session)):
    return await RoleService(db).get_roles()


@router.post("/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_session)):
    return await UserService(db).create_user(user_data)


@router.get("/users", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_session)):
    return await UserService(db).get_users()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, db: AsyncSession = Depends(get_session)):
    return await UserService(db).get_user(user_id)


@router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate, db: AsyncSession = Depends(get_session)):
    return await UserService(db).update_user(user_id, user_data)


@router.post("/login")
async def login(user_data: LoginSchema, db: AsyncSession = Depends(get_session)):
    return await UserService(db).login_user(user_data)
