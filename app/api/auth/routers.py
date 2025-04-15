from email.policy import HTTP
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.schemas import LoginSchema, RoleCreate, RoleResponse, UserCreate, UserResponse, UserUpdate
from app.api.auth.services import RoleService, UserService
from app.core.database import get_session
from app.utils.security import can_create_user, get_current_user


role_router = APIRouter(tags=["Role"])

'''
============================================
Role Routers
===========================================

'''
@role_router.get("/roles", response_model=List[RoleResponse],status_code=status.HTTP_200_OK)
async def get_roles(db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await RoleService(db).get_roles()

@role_router.post("/roles",status_code=status.HTTP_201_CREATED)
async def create_role(data: RoleCreate, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await RoleService(db).create_role(data)

@role_router.get("/roles/{role_id}", response_model=RoleResponse,status_code=status.HTTP_200_OK)
async def get_role_by_id(role_id: str, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await RoleService(db).get_role(role_id)

@role_router.put("/roles/{role_id}", status_code=status.HTTP_200_OK)
async def update_role(role_id: str, role_data: RoleCreate, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await RoleService(db).update_role(role_id, role_data)

@role_router.delete("/roles/{role_id}",status_code=status.HTTP_200_OK)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await RoleService(db).delete_role(role_id)


'''
============================================
User Routers
===========================================

'''

user_router = APIRouter(tags=["User"])

@user_router.get("/users/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user=Depends(get_current_user)):
    return current_user

@user_router.post("/users",status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_session),current_user = Depends(get_current_user)):
    if not can_create_user(current_user, user_data.role_id):
        raise HTTPException(status_code=403, detail=f"You are not authorized to create this Role")
    return await UserService(db).create_user(user_data)


@user_router.get("/users", response_model=List[UserResponse],status_code=status.HTTP_200_OK)
async def get_users(current_user=Depends(get_current_user),db: AsyncSession = Depends(get_session)):
    if current_user.role.name == "admin":
        return await UserService(db).get_users()
    elif current_user.role.name == "hod":
        return await UserService(db).get_users_by_hod(current_user.id)
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")


@user_router.get("/users/{user_id}", response_model=UserResponse,status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str,current_user=Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await UserService(db).get_user(user_id)


@user_router.put("/users/{user_id}",status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user_data: UserUpdate, current_user=Depends(get_current_user),db: AsyncSession = Depends(get_session)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await UserService(db).update_user(user_id, user_data)

@user_router.delete("/users/{user_id}",status_code=status.HTTP_200_OK)
async def delete_user(user_id: str,current_user=Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return await UserService(db).delete_user(user_id)


'''
============================================
Login Routers
===========================================

'''

@user_router.post("/users/login")
async def login(user_data: LoginSchema, db: AsyncSession = Depends(get_session)):
    return await UserService(db).login_user(user_data)