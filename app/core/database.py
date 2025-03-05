from typing import AsyncGenerator, Optional
import uuid

from sqlalchemy import UUID, DateTime, func
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import as_declarative, declarative_base
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings import settings


def create_engine(url, **kwargs):
    """Create an asynchronous SQLAlchemy engine."""
    return create_async_engine(url, echo=False, **kwargs)


# ✅ Add `expire_on_commit=False` to prevent session expiration
master_db_engine = create_engine(settings.postgresql_database_url)

# ✅ Add `expire_on_commit=False`
async_master_session = async_sessionmaker(
    bind=master_db_engine, autocommit=False, autoflush=False, expire_on_commit=False
)

# ✅ Provide correct session management
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide a write database session.
    """
    async with async_master_session() as session:
        try:
            yield session  # ✅ Correct session management
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


Base = declarative_base()


@as_declarative()
class Base:
    '''
    =====================================================
    # Base model to include default columns for all tables.
    =====================================================
    '''
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.timezone('Asia/Kolkata', func.now()))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.timezone('Asia/Kolkata', func.now()), onupdate=func.timezone('Asia/Kolkata', func.now()))
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)  # Track the creator
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)  # Track the updater
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)  # Soft delete column