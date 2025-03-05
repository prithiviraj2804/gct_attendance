

from fastapi import HTTPException
from sqlalchemy import select

from app.api.auth.models import Role, User
from app.utils.password_utils import get_password_hash


class RoleService:
    def __init__(self, db):
        self.db = db

    async def get_roles(self):
        result = await self.db.execute(select(Role))
        roles = result.scalars().all()
        return roles


class UserService:
    def __init__(self, db):
        self.db = db

    async def create_user(self, user_data):
        existing_user = await self.db.execute(select(User).where(User.username == user_data.username))
        if existing_user.scalars().first():
            raise HTTPException(
                detail={"message": "User Already Exists"},
                status_code=403
            )

        new_user = User(**user_data.dict())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return {"message": "User Created Successfully"}

    async def get_users(self):
        result = await self.db.execute(select(User))
        users = result.scalars().all()
        return users
    
    async def get_user(self, user_id):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user
    
    async def update_user(self, user_id, user_data):
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(
                detail={"message": "User Not Found"},
                status_code=404
            )
        
        await self.db.execute(
                User.__table__.update().where(User.id == user_id).values(**user_data.dict())
                )
        await self.db.commit()
        return {"message": "User record updated successfully"}

