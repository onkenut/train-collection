import io
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.export_service import (
    export_page_markdown, export_page_html, export_page_pdf, export_notebook_zip,
)
from ..services.import_service import import_markdown, import_notion

router = APIRouter(prefix="/api", tags=["import_export"])


@router.post("/import/markdown")
async def import_md(
    notebook_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    nb_result = await db.execute(text("SELECT id FROM notebooks WHERE id=:id"), {"id": notebook_id})
    if not nb_result.fetchone():
        raise HTTPException(status_code=404, detail="Notebook not found")

    file_data = []
    for f in files:
        content = await f.read()
        file_data.append((f.filename or "untitled.md", content.decode("utf-8", errors="replace")))

    page_ids = await import_markdown(db, notebook_id, file_data)
    return {"imported": len(page_ids), "page_ids": page_ids}


@router.post("/import/notion")
async def import_notion_data(
    notebook_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    nb_result = await db.execute(text("SELECT id FROM notebooks WHERE id=:id"), {"id": notebook_id})
    if not nb_result.fetchone():
        raise HTTPException(status_code=404, detail="Notebook not found")

    content = await file.read()
    try:
        notion_data = json.loads(content.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Notion export JSON")

    page_ids = await import_notion(db, notebook_id, notion_data)
    return {"imported": len(page_ids), "page_ids": page_ids}


@router.get("/pages/{page_id}/export")
async def export_page(
    page_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db),
):
    if format == "markdown":
        md = await export_page_markdown(db, page_id)
        return StreamingResponse(
            io.BytesIO(md.encode("utf-8")),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=page_{page_id}.md"},
        )
    elif format == "html":
        html = await export_page_html(db, page_id)
        return StreamingResponse(
            io.BytesIO(html.encode("utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=page_{page_id}.html"},
        )
    elif format == "pdf":
        try:
            pdf_bytes = await export_page_pdf(db, page_id)
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=page_{page_id}.pdf"},
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.post("/notebooks/{notebook_id}/export")
async def export_notebook(notebook_id: str, db: AsyncSession = Depends(get_db)):
    nb_result = await db.execute(text("SELECT id FROM notebooks WHERE id=:id"), {"id": notebook_id})
    if not nb_result.fetchone():
        raise HTTPException(status_code=404, detail="Notebook not found")

    try:
        zip_bytes = await export_notebook_zip(db, notebook_id)
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=notebook_{notebook_id}.zip"},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
