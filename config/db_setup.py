import asyncio
from sqlalchemy.orm import Session
from config.database import Base, engine  # Import Base and engine from your main database module

async def init_db():
   async with engine.begin() as conn:
        # Create tables (the async context manager will handle commits)
        await conn.run_sync(Base.metadata.create_all)

# Entry point for running the setup
if __name__ == "__main__":
    asyncio.run(init_db())