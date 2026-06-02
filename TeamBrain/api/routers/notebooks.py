from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Notebook
from ..schemas import NotebookCreate, NotebookUpdate, NotebookOut, ReorderRequest

router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookOut])
async def list_notebooks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM notebooks ORDER BY sort_order"))
    rows = result.fetchall()
    return [NotebookOut(
        id=r[0], name=r[1], icon=r[2], cover_color=r[3],
        sort_order=r[4], created_at=r[5], updated_at=r[6],
    ) for r in rows]


@router.post("", response_model=NotebookOut, status_code=201)
async def create_notebook(body: NotebookCreate, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    result = await db.execute(text("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM notebooks"))
    sort_order = result.scalar()
    nb = Notebook(
        name=body.name, icon=body.icon, cover_color=body.cover_color,
        sort_order=sort_order, created_at=now, updated_at=now,
    )
    db.add(nb)
    await db.commit()
    await db.refresh(nb)
    return nb


@router.put("/{notebook_id}", response_model=NotebookOut)
async def update_notebook(notebook_id: str, body: NotebookUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM notebooks WHERE id=:id"), {"id": notebook_id})
    row = result.fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notebook not found")

    now = datetime.now(timezone.utc).isoformat()
    updates = {"updated_at": now}
    if body.name is not None:
        updates["name"] = body.name
    if body.icon is not None:
        updates["icon"] = body.icon
    if body.cover_color is not None:
        updates["cover_color"] = body.cover_color

    set_clause = ", ".join(f"{k}=:{k}" for k in updates)
    updates["id"] = notebook_id
    await db.execute(text(f"UPDATE notebooks SET {set_clause} WHERE id=:id"), updates)
    await db.commit()

    result = await db.execute(text("SELECT * FROM notebooks WHERE id=:id"), {"id": notebook_id})
    r = result.fetchone()
    return NotebookOut(
        id=r[0], name=r[1], icon=r[2], cover_color=r[3],
        sort_order=r[4], created_at=r[5], updated_at=r[6],
    )


@router.delete("/{notebook_id}", status_code=204)
async def delete_notebook(notebook_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT id FROM notebooks WHERE id=:id"), {"id": notebook_id})
    if not result.fetchone():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notebook not found")
    await db.execute(text("DELETE FROM notebooks WHERE id=:id"), {"id": notebook_id})
    await db.commit()


@router.put("/reorder", status_code=204)
async def reorder_notebooks(body: ReorderRequest, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc).isoformat()
    for item in body.items:
        await db.execute(
            text("UPDATE notebooks SET sort_order=:so, updated_at=:ua WHERE id=:id"),
            {"so": item.sort_order, "ua": now, "id": item.id},
        )
    await db.commit()
