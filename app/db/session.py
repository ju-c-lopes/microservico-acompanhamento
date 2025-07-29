import os
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", None)
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. Please configure it before running the application."
    )

# Sync engine para compatibilidade com código existente
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine e session para novos endpoints
# Converte URLs para drivers async
async_url = SQLALCHEMY_DATABASE_URL
if async_url.startswith("mysql://"):
    async_url = async_url.replace("mysql://", "mysql+aiomysql://")
elif async_url.startswith("sqlite://"):
    async_url = async_url.replace("sqlite://", "sqlite+aiosqlite://")
elif async_url.startswith("postgresql://"):
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    async_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Gerador de sessões assíncronas para uso em endpoints FastAPI.
    """
    async with async_session() as session:
        yield session
