import io
import json
import os
import zipfile
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import ATTACHMENTS_DIR


def blocks_to_markdown(blocks: list[dict]) -> str:
    lines = []
    for block in blocks:
        btype = block.get("type", "paragraph")
        content = block.get("content", "")
        if btype == "heading1":
            lines.append(f"# {content}")
        elif btype == "heading2":
            lines.append(f"## {content}")
        elif btype == "heading3":
            lines.append(f"### {content}")
        elif btype == "paragraph":
            lines.append(content)
        elif btype == "bullet_list":
            lines.append(f"- {content}")
        elif btype == "ordered_list":
            lines.append(f"1. {content}")
        elif btype == "task_list":
            checked = block.get("properties", {}).get("checked", False)
            mark = "x" if checked else " "
            lines.append(f"- [{mark}] {content}")
        elif btype == "blockquote":
            lines.append(f"> {content}")
        elif btype == "divider":
            lines.append("---")
        elif btype == "code":
            lang = block.get("properties", {}).get("language", "")
            lines.append(f"```{lang}\n{content}\n```")
        elif btype == "math":
            lines.append(f"$$\n{content}\n$$")
        elif btype == "mermaid":
            lines.append(f"```mermaid\n{content}\n```")
        elif btype == "table":
            lines.append(content)
        elif btype == "image":
            lines.append(f"![{content}]({content})")
        elif btype == "file":
            lines.append(f"[{content}]({content})")
        else:
            lines.append(content)
        lines.append("")
    return "\n".join(lines)


def blocks_to_html(title: str, blocks: list[dict]) -> str:
    body_parts = []
    for block in blocks:
        btype = block.get("type", "paragraph")
        content = block.get("content", "")
        if btype == "heading1":
            body_parts.append(f"<h1>{content}</h1>")
        elif btype == "heading2":
            body_parts.append(f"<h2>{content}</h2>")
        elif btype == "heading3":
            body_parts.append(f"<h3>{content}</h3>")
        elif btype == "paragraph":
            body_parts.append(f"<p>{content}</p>")
        elif btype == "bullet_list":
            body_parts.append(f"<ul><li>{content}</li></ul>")
        elif btype == "ordered_list":
            body_parts.append(f"<ol><li>{content}</li></ol>")
        elif btype == "task_list":
            checked = block.get("properties", {}).get("checked", False)
            mark = "checked" if checked else ""
            body_parts.append(f'<div><input type="checkbox" {mark} disabled /> {content}</div>')
        elif btype == "blockquote":
            body_parts.append(f"<blockquote>{content}</blockquote>")
        elif btype == "divider":
            body_parts.append("<hr />")
        elif btype == "code":
            body_parts.append(f"<pre><code>{content}</code></pre>")
        elif btype == "math":
            body_parts.append(f'<div class="math">{content}</div>')
        elif btype == "image":
            body_parts.append(f'<img src="{content}" alt="{content}" />')
        elif btype == "file":
            body_parts.append(f'<a href="{content}">{content}</a>')
        else:
            body_parts.append(f"<p>{content}</p>")

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><title>{title}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:20px;}}
blockquote{{border-left:3px solid #ccc;padding-left:10px;color:#555;}}
pre{{background:#f5f5f5;padding:10px;border-radius:4px;overflow-x:auto;}}</style>
</head>
<body>{"".join(body_parts)}</body></html>"""


async def export_page_markdown(db: AsyncSession, page_id: str) -> str:
    page_result = await db.execute(text("SELECT title FROM pages WHERE id=:pid"), {"pid": page_id})
    page_row = page_result.fetchone()
    if not page_row:
        raise ValueError("Page not found")
    title = page_row[0]

    blocks_result = await db.execute(
        text("SELECT type, content, properties FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
        {"pid": page_id},
    )
    blocks = [
        {"type": r[0], "content": r[1], "properties": json.loads(r[2]) if r[2] else {}}
        for r in blocks_result.fetchall()
    ]

    md = f"# {title}\n\n{blocks_to_markdown(blocks)}"
    return md


async def export_page_html(db: AsyncSession, page_id: str) -> str:
    page_result = await db.execute(text("SELECT title FROM pages WHERE id=:pid"), {"pid": page_id})
    page_row = page_result.fetchone()
    if not page_row:
        raise ValueError("Page not found")
    title = page_row[0]

    blocks_result = await db.execute(
        text("SELECT type, content, properties FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
        {"pid": page_id},
    )
    blocks = [
        {"type": r[0], "content": r[1], "properties": json.loads(r[2]) if r[2] else {}}
        for r in blocks_result.fetchall()
    ]

    return blocks_to_html(title, blocks)


async def export_page_pdf(db: AsyncSession, page_id: str) -> bytes:
    html = await export_page_html(db, page_id)
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except ImportError:
        raise ValueError("weasyprint is not installed. Install it to enable PDF export.")


async def export_notebook_zip(db: AsyncSession, notebook_id: str) -> bytes:
    pages_result = await db.execute(
        text("SELECT id, title FROM pages WHERE notebook_id=:nid AND is_template=0 ORDER BY sort_order"),
        {"nid": notebook_id},
    )
    pages = pages_result.fetchall()
    if not pages:
        raise ValueError("No pages found in notebook")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for page in pages:
            md = await export_page_markdown(db, page[0])
            safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in page[1])
            zf.writestr(f"{safe_name}.md", md)

    return buf.getvalue()
