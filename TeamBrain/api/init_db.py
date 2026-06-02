import asyncio
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal, engine
from .models import Base


DEFAULT_SETTINGS = {
    "ai_api_key": "",
    "ai_base_url": "https://api.openai.com/v1",
    "ai_model": "gpt-3.5-turbo",
    "ai_monthly_budget": "1000000",
}

DEFAULT_NOTEBOOKS = [
    {
        "id": "default",
        "name": "默认笔记本",
        "icon": "\U0001f4d3",
        "cover_color": "#10B981",
        "sort_order": 0,
    }
]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pages_fts'"
        ))
        if not result.fetchone():
            await conn.execute(text("""
                CREATE VIRTUAL TABLE pages_fts USING fts5(
                    title,
                    content,
                    ai_summary,
                    content='pages',
                    content_rowid='rowid',
                    tokenize='unicode61'
                )
            """))
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA foreign_keys=ON"))

        result = await conn.execute(text("PRAGMA table_info(pages)"))
        columns = [row[1] for row in result.fetchall()]
        if 'content' not in columns:
            await conn.execute(text("ALTER TABLE pages ADD COLUMN content TEXT NOT NULL DEFAULT ''"))
        if 'ai_summary' not in columns:
            await conn.execute(text("ALTER TABLE pages ADD COLUMN ai_summary TEXT"))


async def insert_default_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM notebooks"))
        count = result.scalar()
        if count == 0:
            from .models import Notebook, Setting
            now = datetime.now(timezone.utc).isoformat()
            for nb in DEFAULT_NOTEBOOKS:
                session.add(Notebook(
                    id=nb["id"],
                    name=nb["name"],
                    icon=nb["icon"],
                    cover_color=nb["cover_color"],
                    sort_order=nb["sort_order"],
                    created_at=now,
                    updated_at=now,
                ))
            for key, value in DEFAULT_SETTINGS.items():
                session.add(Setting(key=key, value=value, updated_at=now))
            await session.commit()


async def init_db():
    await create_tables()
    await insert_default_data()


if __name__ == "__main__":
    asyncio.run(init_db())
