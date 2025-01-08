from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import Database

DATABASE_URL = "postgresql+asyncpg://postgres:310302@localhost:5432/Teaching"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# Define the base class for models
Base = declarative_base()

# Async database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
 
        # "postgresql://postgres:310302@localhost:5432/Teaching"