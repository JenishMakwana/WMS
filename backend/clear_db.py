import asyncio
import sys
import os

sys.path.append(os.getcwd())

from sqlalchemy import text
from app.db.session import engine, Base
import app.models

async def clear_db():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        # Manually drop alembic_version
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        print("Database cleared successfully.")

if __name__ == '__main__':
    asyncio.run(clear_db())
