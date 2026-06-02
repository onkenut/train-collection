import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Page, Block
from ..schemas import SyncPayload, SyncChangesResponse, SyncChangeItem

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("")
async def sync_pages(body: SyncPayload, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    updated_ids = []

    for item in body.pages:
        result = await db.execute(text("SELECT id, updated_at FROM pages WHERE id=:id"), {"id": item.id})
        existing = result.fetchone()

        if existing:
            existing_updated = existing[1]
            if item.updated_at >= existing_updated:
                await db.execute(
                    text("UPDATE pages SET title=:t, updated_at=:ua WHERE id=:id"),
                    {"t": item.title, "ua": item.updated_at, "id": item.id},
                )
                await db.execute(text("DELETE FROM blocks WHERE page_id=:pid"), {"pid": item.id})
                for j, block_data in enumerate(item.blocks):
                    block = Block(
                        page_id=item.id,
                        type=block_data.type,
                        content=block_data.content,
                        properties=json.dumps(block_data.properties),
                        sort_order=block_data.sort_order or j,
                        parent_block_id=block_data.parent_block_id,
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(block)
                updated_ids.append(item.id)
        else:
            page_result = await db.execute(text("SELECT id FROM pages WHERE id=:id"), {"id": item.id})
            if not page_result.fetchone():
                nb_result = await db.execute(text("SELECT id FROM notebooks LIMIT 1"))
                nb_row = nb_result.fetchone()
                notebook_id = nb_row[0] if nb_row else "default"

                page = Page(
                    id=item.id,
                    notebook_id=notebook_id,
                    title=item.title,
                    created_at=now,
                    updated_at=item.updated_at,
                )
                db.add(page)
                await db.flush()

                for j, block_data in enumerate(item.blocks):
                    block = Block(
                        page_id=item.id,
                        type=block_data.type,
                        content=block_data.content,
                        properties=json.dumps(block_data.properties),
                        sort_order=block_data.sort_order or j,
                        parent_block_id=block_data.parent_block_id,
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(block)
                updated_ids.append(item.id)

    await db.commit()

    from ..services.search_service import rebuild_fts
    for pid in updated_ids:
        await rebuild_fts(db, pid)

    return {"synced": len(updated_ids), "page_ids": updated_ids}


@router.get("/changes", response_model=SyncChangesResponse)
async def get_changes(since: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT id, title, updated_at FROM pages WHERE updated_at > :since ORDER BY updated_at"),
        {"since": since},
    )
    changes = []
    for r in result.fetchall():
        changes.append(SyncChangeItem(
            id=r[0], title=r[1], updated_at=r[2], action="updated",
        ))

    deleted_result = await db.execute(
        text("SELECT id, '' as title, updated_at FROM pages WHERE updated_at > :since"),
        {"since": since},
    )

    return SyncChangesResponse(changes=changes, since=since)
