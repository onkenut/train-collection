import difflib
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import PageVersion, Page, Block
from ..schemas import VersionOut, VersionDiffOut

router = APIRouter(prefix="/api", tags=["versions"])


@router.get("/pages/{page_id}/versions", response_model=list[VersionOut])
async def list_versions(page_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM page_versions WHERE page_id=:pid ORDER BY created_at DESC"),
        {"pid": page_id},
    )
    return [VersionOut(id=r[0], page_id=r[1], snapshot=r[2], char_count=r[3], created_at=r[4])
            for r in result.fetchall()]


@router.get("/versions/{version_id}", response_model=VersionOut)
async def get_version(version_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM page_versions WHERE id=:id"), {"id": version_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Version not found")
    return VersionOut(id=r[0], page_id=r[1], snapshot=r[2], char_count=r[3], created_at=r[4])


@router.post("/versions/{version_id}/restore")
async def restore_version(version_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM page_versions WHERE id=:id"), {"id": version_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Version not found")

    page_id = r[1]
    snapshot = json.loads(r[2])
    now = datetime.now(timezone.utc).isoformat()

    await db.execute(text("DELETE FROM blocks WHERE page_id=:pid"), {"pid": page_id})

    for block_data in snapshot.get("blocks", []):
        block = Block(
            page_id=page_id,
            type=block_data.get("type", "paragraph"),
            content=block_data.get("content", ""),
            properties=json.dumps(block_data.get("properties", {})),
            sort_order=block_data.get("sort_order", 0),
            parent_block_id=block_data.get("parent_block_id"),
            created_at=now,
            updated_at=now,
        )
        db.add(block)

    await db.execute(
        text("UPDATE pages SET updated_at=:ua WHERE id=:id"),
        {"ua": now, "id": page_id},
    )
    await db.commit()

    from ..services.search_service import rebuild_fts
    await rebuild_fts(db, page_id)

    return {"status": "restored", "page_id": page_id}


@router.post("/versions/{version_id}/copy")
async def copy_version(version_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM page_versions WHERE id=:id"), {"id": version_id})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Version not found")

    page_id = r[1]
    page_result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    pr = page_result.fetchone()
    if not pr:
        raise HTTPException(status_code=404, detail="Source page not found")

    now = datetime.now(timezone.utc).isoformat()
    sort_result = await db.execute(
        text("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM pages WHERE notebook_id=:nid"),
        {"nid": pr[1]},
    )
    sort_order = sort_result.scalar()

    new_page = Page(
        notebook_id=pr[1],
        title=f"{pr[3]} (副本)",
        icon=pr[4],
        sort_order=sort_order,
        is_template=False,
        metadata_=pr[7],
        created_at=now,
        updated_at=now,
    )
    db.add(new_page)
    await db.flush()

    snapshot = json.loads(r[2])
    for block_data in snapshot.get("blocks", []):
        block = Block(
            page_id=new_page.id,
            type=block_data.get("type", "paragraph"),
            content=block_data.get("content", ""),
            properties=json.dumps(block_data.get("properties", {})),
            sort_order=block_data.get("sort_order", 0),
            parent_block_id=block_data.get("parent_block_id"),
            created_at=now,
            updated_at=now,
        )
        db.add(block)

    await db.commit()
    return {"status": "copied", "new_page_id": new_page.id}


@router.get("/versions/{version_id}/diff", response_model=VersionDiffOut)
async def diff_versions(
    version_id: str,
    target_version_id: str,
    db: AsyncSession = Depends(get_db),
):
    result1 = await db.execute(text("SELECT * FROM page_versions WHERE id=:id"), {"id": version_id})
    r1 = result1.fetchone()
    if not r1:
        raise HTTPException(status_code=404, detail="Source version not found")

    result2 = await db.execute(text("SELECT * FROM page_versions WHERE id=:id"), {"id": target_version_id})
    r2 = result2.fetchone()
    if not r2:
        raise HTTPException(status_code=404, detail="Target version not found")

    lines1 = r1[2].splitlines()
    lines2 = r2[2].splitlines()
    diff_lines = list(difflib.unified_diff(lines1, lines2, lineterm=""))

    return VersionDiffOut(
        source_version_id=version_id,
        target_version_id=target_version_id,
        diff=diff_lines,
    )
