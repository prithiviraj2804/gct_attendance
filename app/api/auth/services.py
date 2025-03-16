

from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select

from app.api.auth.models import Role, User
from app.utils.password_utils import get_password_hash,verify_password
from app.utils.security import create_access_token


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

        new_user = User(username=user_data.username,
                        name=user_data.name,
                        password=get_password_hash(user_data.password),
                        role_id=user_data.role_id,
                        section_id=user_data.section_id)
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

        # Fetch the user from the database
        query = await self.db.execute(select(User).where(User.id == user_id))
        user = query.scalars().first()
        if not user:
            raise HTTPException(
                detail={"message": "User Not Found"},
                status_code=404
            )

        # Prepare a dictionary of fields to be updated
        update_fields = {}

        if user_data.username is not None:
            update_fields["username"] = user_data.username
        if user_data.name is not None:
            update_fields["name"] = user_data.name
        if user_data.password is not None:
            update_fields["password"] = user_data.password
        if user_data.role_id is not None:
            update_fields["role_id"] = user_data.role_id

        if user_data.section_id is not None:
            update_fields["section_id"] = user_data.section_id

        # Only proceed if there are fields to update
        if update_fields:
            await self.db.execute(
                User.__table__.update().where(User.id == user_id).values(update_fields)
            )
            await self.db.commit()
            return {"message": "User record updated successfully"}

        raise HTTPException(
            detail="No fields to update",
            status_code=400
        )

    async def login_user(self, user_data):
        result = await self.db.execute(select(User).where(User.username == user_data.username))
        user = result.scalars().first()
        if not verify_password(user_data.password, user.password):
            raise HTTPException(
                detail="Invalid username or password",
                status_code=401
            )
        access_token = create_access_token({"id": str(user.id)}, expires_delta=timedelta(hours=1))
        return {"access_token": access_token, "token_type": "bearer"}