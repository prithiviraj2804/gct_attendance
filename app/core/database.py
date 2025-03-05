from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from typing import AsyncGenerator


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
