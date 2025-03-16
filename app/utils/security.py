from datetime import datetime, timedelta, timezone
import os
from typing import Optional
from jose import jwt
from sqlalchemy import select
from app.core.settings import settings
import hashlib
import hmac
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError
from app.api.auth.models import User
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


'''
=====================================================
# Create JWT token
=====================================================
'''


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


'''
=====================================================
# Decode JWT token
=====================================================
'''


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: AsyncSession = Depends(get_session)
):
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )