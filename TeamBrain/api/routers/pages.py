import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Page, Block, PageVersion
from ..schemas import PageCreate, PageUpdate, PageOut, PageMove, PageSaveRequest, BlockOut
from ..services.search_service import rebuild_fts

router = APIRouter(prefix="/api", tags=["pages"])


def _row_to_page_out(r) -> dict:
    meta = {}
    try:
        meta = json.loads(r[7]) if r[7] else {}
    except Exception:
        pass
    return {
        "id": r[0], "notebook_id": r[1], "parent_id": r[2],
        "title": r[3], "icon": r[4], "sort_order": r[5],
        "is_template": bool(r[6]), "metadata": meta,
        "created_at": r[8], "updated_at": r[9],
    }


@router.get("/notebooks/{notebook_id}/pages", response_model=list[PageOut])
async def list_pages(notebook_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM pages WHERE notebook_id=:nid ORDER BY sort_order"),
        {"nid": notebook_id},
    )
    return [_row_to_page_out(r) for r in result.fetchall()]


@router.post("/notebooks/{notebook_id}/pages", response_model=PageOut, status_code=201)
async def create_page(notebook_id: str, body: PageCreate, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    result = await db.execute(
        text("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM pages WHERE notebook_id=:nid"),
        {"nid": notebook_id},
    )
    sort_order = result.scalar()

    page = Page(
        notebook_id=notebook_id,
        parent_id=body.parent_id,
        title=body.title,
        icon=body.icon,
        sort_order=sort_order,
        is_template=body.is_template,
        metadata_=json.dumps(body.metadata),
        created_at=now,
        updated_at=now,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return PageOut(
        id=page.id, notebook_id=page.notebook_id, parent_id=page.parent_id,
        title=page.title, icon=page.icon, sort_order=page.sort_order,
        is_template=page.is_template, metadata=json.loads(page.metadata_) if page.metadata_ else {},
        created_at=page.created_at, updated_at=page.updated_at,
    )


@router.get("/pages/{page_id}")
async def get_page(page_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Page not found")

    page_data = _row_to_page_out(r)

    blocks_result = await db.execute(
        text("SELECT * FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
        {"pid": page_id},
    )
    blocks = []
    for br in blocks_result.fetchall():
        props = {}
        try:
            props = json.loads(br[4]) if br[4] else {}
        except Exception:
            pass
        blocks.append(BlockOut(
            id=br[0], page_id=br[1], type=br[2], content=br[3],
            properties=props, sort_order=br[5], parent_block_id=br[6],
            created_at=br[7], updated_at=br[8],
        ))

    page_data["blocks"] = blocks
    return page_data


@router.put("/pages/{page_id}", response_model=PageOut)
async def update_page(page_id: str, body: PageUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Page not found")

    now = datetime.now(timezone.utc).isoformat()
    updates = {"updated_at": now}
    if body.title is not None:
        updates["title"] = body.title
    if body.icon is not None:
        updates["icon"] = body.icon
    if body.parent_id is not None:
        updates["parent_id"] = body.parent_id
    if body.is_template is not None:
        updates["is_template"] = int(body.is_template)
    if body.metadata is not None:
        updates["metadata"] = json.dumps(body.metadata)

    set_clause = ", ".join(f"{k}=:{k}" for k in updates)
    updates["id"] = page_id
    await db.execute(text(f"UPDATE pages SET {set_clause} WHERE id=:id"), updates)
    await db.commit()

    result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    return _row_to_page_out(result.fetchone())


@router.delete("/pages/{page_id}", status_code=204)
async def delete_page(page_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT id FROM pages WHERE id=:id"), {"id": page_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Page not found")
    await db.execute(text("DELETE FROM pages_fts WHERE rowid=:rid"), {"rid": page_id})
    await db.execute(text("DELETE FROM pages WHERE id=:id"), {"id": page_id})
    await db.commit()


@router.put("/pages/{page_id}/move", response_model=PageOut)
async def move_page(page_id: str, body: PageMove, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Page not found")

    now = datetime.now(timezone.utc).isoformat()
    updates = {"notebook_id": body.notebook_id, "updated_at": now}
    if body.parent_id is not None:
        updates["parent_id"] = body.parent_id
    if body.sort_order is not None:
        updates["sort_order"] = body.sort_order

    set_clause = ", ".join(f"{k}=:{k}" for k in updates)
    updates["id"] = page_id
    await db.execute(text(f"UPDATE pages SET {set_clause} WHERE id=:id"), updates)
    await db.commit()

    result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    return _row_to_page_out(result.fetchone())


@router.post("/pages/{page_id}/save")
async def save_page(page_id: str, body: PageSaveRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Page not found")

    now = datetime.now(timezone.utc).isoformat()

    page_updates = {"updated_at": now}
    if body.title is not None:
        page_updates["title"] = body.title
    if body.icon is not None:
        page_updates["icon"] = body.icon
    set_clause = ", ".join(f"{k}=:{k}" for k in page_updates)
    page_updates["id"] = page_id
    await db.execute(text(f"UPDATE pages SET {set_clause} WHERE id=:id"), page_updates)

    old_blocks = await db.execute(
        text("SELECT id, type, content, properties, sort_order, parent_block_id FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
        {"pid": page_id},
    )
    old_rows = old_blocks.fetchall()
    snapshot_blocks = [
        {"id": row[0], "type": row[1], "content": row[2],
         "properties": json.loads(row[3]) if row[3] else {}, "sort_order": row[4],
         "parent_block_id": row[5]}
        for row in old_rows
    ]
    snapshot = json.dumps({"page_id": page_id, "blocks": snapshot_blocks}, ensure_ascii=False)
    char_count = sum(len(row[2] or "") for row in old_rows)

    version = PageVersion(
        page_id=page_id, snapshot=snapshot, char_count=char_count, created_at=now,
    )
    db.add(version)

    await db.execute(text("DELETE FROM blocks WHERE page_id=:pid"), {"pid": page_id})

    for i, block_data in enumerate(body.blocks):
        block = Block(
            page_id=page_id,
            type=block_data.type,
            content=block_data.content,
            properties=json.dumps(block_data.properties),
            sort_order=block_data.sort_order or i,
            parent_block_id=block_data.parent_block_id,
            created_at=now,
            updated_at=now,
        )
        db.add(block)

    await db.commit()
    await rebuild_fts(db, page_id)

    return {"status": "saved", "version_id": version.id}


@router.post("/pages/from-template/{template_id}", response_model=PageOut, status_code=201)
async def create_from_template(template_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM pages WHERE id=:id AND is_template=1"), {"id": template_id})
    tpl = result.fetchone()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    now = datetime.now(timezone.utc).isoformat()
    sort_result = await db.execute(
        text("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM pages WHERE notebook_id=:nid"),
        {"nid": tpl[1]},
    )
    sort_order = sort_result.scalar()

    new_page = Page(
        notebook_id=tpl[1],
        parent_id=None,
        title=tpl[3] + " (副本)",
        icon=tpl[4],
        sort_order=sort_order,
        is_template=False,
        metadata_=tpl[7],
        created_at=now,
        updated_at=now,
    )
    db.add(new_page)
    await db.flush()

    blocks_result = await db.execute(
        text("SELECT type, content, properties, sort_order, parent_block_id FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
        {"pid": template_id},
    )
    for br in blocks_result.fetchall():
        block = Block(
            page_id=new_page.id,
            type=br[0], content=br[1],
            properties=br[2],
            sort_order=br[3],
            parent_block_id=br[4],
            created_at=now, updated_at=now,
        )
        db.add(block)

    await db.commit()
    await db.refresh(new_page)
    return PageOut(
        id=new_page.id, notebook_id=new_page.notebook_id, parent_id=new_page.parent_id,
        title=new_page.title, icon=new_page.icon, sort_order=new_page.sort_order,
        is_template=new_page.is_template,
        metadata=json.loads(new_page.metadata_) if new_page.metadata_ else {},
        created_at=new_page.created_at, updated_at=new_page.updated_at,
    )
