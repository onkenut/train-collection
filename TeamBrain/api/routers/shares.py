import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ShareLink, Page, Block
from ..schemas import ShareLinkCreate, ShareLinkOut, ShareAccessRequest

router = APIRouter(prefix="/api", tags=["shares"])


@router.post("/pages/{page_id}/share", response_model=ShareLinkOut)
async def create_share_link(page_id: str, body: ShareLinkCreate, db: AsyncSession = Depends(get_db)):
    page_result = await db.execute(text("SELECT id FROM pages WHERE id=:id"), {"id": page_id})
    if not page_result.fetchone():
        raise HTTPException(status_code=404, detail="Page not found")

    now = datetime.now(timezone.utc).isoformat()
    share = ShareLink(
        page_id=page_id,
        password=body.password,
        expires_at=body.expires_at,
        created_at=now,
    )
    db.add(share)
    await db.commit()
    await db.refresh(share)
    return ShareLinkOut(
        id=share.id, page_id=share.page_id, token=share.token,
        password=share.password, expires_at=share.expires_at, created_at=share.created_at,
    )


@router.get("/shares", response_model=list[ShareLinkOut])
async def list_shares(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM share_links ORDER BY created_at DESC"))
    return [
        ShareLinkOut(id=r[0], page_id=r[1], token=r[2], password=r[3], expires_at=r[4], created_at=r[5])
        for r in result.fetchall()
    ]


@router.delete("/shares/{share_id}", status_code=204)
async def delete_share_link(share_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT id FROM share_links WHERE id=:id"), {"id": share_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Share link not found")
    await db.execute(text("DELETE FROM share_links WHERE id=:id"), {"id": share_id})
    await db.commit()


@router.get("/share/{token}")
async def access_shared_page(token: str, body: ShareAccessRequest | None = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM share_links WHERE token=:t"), {"t": token})
    r = result.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Share link not found")

    share_id, page_id, share_token, password, expires_at, created_at = r

    if expires_at:
        expires_dt = datetime.fromisoformat(expires_at)
        if datetime.now(timezone.utc) > expires_dt.replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=410, detail="Share link has expired")

    if password:
        request_password = body.password if body else None
        if request_password != password:
            raise HTTPException(status_code=403, detail="Incorrect password")

    page_result = await db.execute(text("SELECT * FROM pages WHERE id=:id"), {"id": page_id})
    pr = page_result.fetchone()
    if not pr:
        raise HTTPException(status_code=404, detail="Page not found")

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
        blocks.append({
            "id": br[0], "page_id": br[1], "type": br[2], "content": br[3],
            "properties": props, "sort_order": br[5], "parent_block_id": br[6],
            "created_at": br[7], "updated_at": br[8],
        })

    meta = {}
    try:
        meta = json.loads(pr[7]) if pr[7] else {}
    except Exception:
        pass

    return {
        "page": {
            "id": pr[0], "notebook_id": pr[1], "parent_id": pr[2],
            "title": pr[3], "icon": pr[4], "content": pr[10] or "",
            "sort_order": pr[5],
            "is_template": bool(pr[6]), "metadata": meta,
            "created_at": pr[8], "updated_at": pr[9],
        },
        "blocks": blocks,
    }
