"""
Database utility module for asynchronous SQLAlchemy sessions.

This module sets up the asynchronous SQLAlchemy engine and sessionmaker for
database interactions. It provides a dependency function for obtaining a
database session in FastAPI endpoints.
"""

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.getenv("DB_USER", "vscode")
DB_PASSWORD = os.getenv("DB_PASSWORD", None)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "authentication-service")

if DB_PASSWORD:
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """
    Dependency that provides a SQLAlchemy asynchronous database session.

    Yields:
        AsyncSession: An active SQLAlchemy async session for database operations.

    Usage:
        Use as a dependency in FastAPI endpoints to access the database.
    """
    async with SessionLocal() as session:
        yield session
