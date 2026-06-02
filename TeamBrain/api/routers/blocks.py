import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Block
from ..schemas import BlockCreate, BlockUpdate, BlockOut, ReorderRequest

router = APIRouter(prefix="/api", tags=["blocks"])


def _row_to_block_out(r) -> BlockOut:
    props = {}
    try:
        props = json.loads(r[4]) if r[4] else {}
    except Exception:
        pass
    return BlockOut(
        id=r[0], page_id=r[1], type=r[2], content=r[3],
        properties=props, sort_order=r[5], parent_block_id=r[6],
        created_at=r[7], updated_at=r[8],
    )


@router.get("/pages/{page_id}/blocks", response_model=list[BlockOut])
async def list_blocks(page_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
        {"pid": page_id},
    )
    return [_row_to_block_out(r) for r in result.fetchall()]


@router.post("/pages/{page_id}/blocks", response_model=BlockOut, status_code=201)
async def create_block(page_id: str, body: BlockCreate, db: AsyncSession = Depends(get_db)):
    page_result = await db.execute(text("SELECT id FROM pages WHERE id=:id"), {"id": page_id})
    if not page_result.fetchone():
        raise HTTPException(status_code=404, detail="Page not found")

    now = datetime.now(timezone.utc).isoformat()
    if body.sort_order == 0:
        result = await db.execute(
            text("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM blocks WHERE page_id=:pid"),
            {"pid": page_id},
        )
        sort_order = result.scalar()
    else:
        sort_order = body.sort_order

    block = Block(
        page_id=page_id,
        type=body.type,
        content=body.content,
        properties=json.dumps(body.properties),
        sort_order=sort_order,
        parent_block_id=body.parent_block_id,
        created_at=now,
        updated_at=now,
    )
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return _row_to_block_out((
        block.id, block.page_id, block.type, block.content,
        block.properties, block.sort_order, block.parent_block_id,
        block.created_at, block.updated_at,
    ))


@router.put("/blocks/{block_id}", response_model=BlockOut)
async def update_block(block_id: str, body: BlockUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM blocks WHERE id=:id"), {"id": block_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Block not found")

    now = datetime.now(timezone.utc).isoformat()
    updates = {"updated_at": now}
    if body.type is not None:
        updates["type"] = body.type
    if body.content is not None:
        updates["content"] = body.content
    if body.properties is not None:
        updates["properties"] = json.dumps(body.properties)
    if body.sort_order is not None:
        updates["sort_order"] = body.sort_order
    if body.parent_block_id is not None:
        updates["parent_block_id"] = body.parent_block_id

    set_clause = ", ".join(f"{k}=:{k}" for k in updates)
    updates["id"] = block_id
    await db.execute(text(f"UPDATE blocks SET {set_clause} WHERE id=:id"), updates)
    await db.commit()

    result = await db.execute(text("SELECT * FROM blocks WHERE id=:id"), {"id": block_id})
    return _row_to_block_out(result.fetchone())


@router.delete("/blocks/{block_id}", status_code=204)
async def delete_block(block_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT id FROM blocks WHERE id=:id"), {"id": block_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Block not found")
    await db.execute(text("DELETE FROM blocks WHERE id=:id"), {"id": block_id})
    await db.commit()


@router.put("/pages/{page_id}/blocks/reorder", status_code=204)
async def reorder_blocks(page_id: str, body: ReorderRequest, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    for item in body.items:
        await db.execute(
            text("UPDATE blocks SET sort_order=:so, updated_at=:ua WHERE id=:id AND page_id=:pid"),
            {"so": item.sort_order, "ua": now, "id": item.id, "pid": page_id},
        )
    await db.commit()
