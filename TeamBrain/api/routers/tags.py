from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Tag, PageTag
from ..schemas import TagCreate, TagOut, PageOut

router = APIRouter(prefix="/api/tags", tags=["tags"])


def _row_to_page_out(r) -> dict:
    import json
    meta = {}
    try:
        meta = json.loads(r[7]) if r[7] else {}
    except Exception:
        pass
    return {
        "id": r[0], "notebook_id": r[1], "parent_id": r[2],
        "title": r[3], "icon": r[4], "content": r[10] or "",
        "sort_order": r[5],
        "is_template": bool(r[6]), "metadata": meta,
        "created_at": r[8], "updated_at": r[9],
    }


@router.get("", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM tags ORDER BY name"))
    return [TagOut(id=r[0], name=r[1], color=r[2], created_at=r[3]) for r in result.fetchall()]


@router.post("/pages/{page_id}/tags", response_model=TagOut)
async def add_tag_to_page(page_id: str, body: TagCreate, db: AsyncSession = Depends(get_db)):
    page_result = await db.execute(text("SELECT id FROM pages WHERE id=:id"), {"id": page_id})
    if not page_result.fetchone():
        raise HTTPException(status_code=404, detail="Page not found")

    tag_result = await db.execute(text("SELECT * FROM tags WHERE name=:name"), {"name": body.name})
    tag_row = tag_result.fetchone()

    if tag_row:
        tag_id = tag_row[0]
    else:
        now = datetime.now(timezone.utc).isoformat()
        tag = Tag(name=body.name, color=body.color, created_at=now)
        db.add(tag)
        await db.flush()
        tag_id = tag.id
        tag_row = (tag.id, tag.name, tag.color, tag.created_at)

    existing = await db.execute(
        text("SELECT id FROM page_tags WHERE page_id=:pid AND tag_id=:tid"),
        {"pid": page_id, "tid": tag_id},
    )
    if existing.fetchone():
        raise HTTPException(status_code=409, detail="Tag already associated with this page")

    now = datetime.now(timezone.utc).isoformat()
    page_tag = PageTag(page_id=page_id, tag_id=tag_id, created_at=now)
    db.add(page_tag)
    await db.commit()

    return TagOut(id=tag_row[0], name=tag_row[1], color=tag_row[2], created_at=tag_row[3])


@router.delete("/pages/{page_id}/tags/{tag_id}", status_code=204)
async def remove_tag_from_page(page_id: str, tag_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT id FROM page_tags WHERE page_id=:pid AND tag_id=:tid"),
        {"pid": page_id, "tid": tag_id},
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Tag association not found")
    await db.execute(
        text("DELETE FROM page_tags WHERE page_id=:pid AND tag_id=:tid"),
        {"pid": page_id, "tid": tag_id},
    )
    await db.commit()


@router.get("/{tag_id}/pages", response_model=list[PageOut])
async def get_pages_by_tag(tag_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT p.* FROM pages p
            JOIN page_tags pt ON pt.page_id = p.id
            WHERE pt.tag_id = :tid
            ORDER BY p.sort_order
        """),
        {"tid": tag_id},
    )
    return [_row_to_page_out(r) for r in result.fetchall()]
