import jieba
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def segment_chinese(query: str) -> str:
    words = jieba.cut(query)
    terms = [w.strip() for w in words if w.strip()]
    return " OR ".join(terms)


async def rebuild_fts(db: AsyncSession, page_id: str):
    page_result = await db.execute(
        text("SELECT title, content, ai_summary FROM pages WHERE id=:pid"), {"pid": page_id}
    )
    page_row = page_result.fetchone()
    if not page_row:
        return

    title = page_row[0] or ""
    content = page_row[1] or ""
    ai_summary = page_row[2] or ""

    if not content:
        blocks_result = await db.execute(
            text("SELECT content FROM blocks WHERE page_id=:pid ORDER BY sort_order"),
            {"pid": page_id},
        )
        content_parts = [row[0] for row in blocks_result.fetchall() if row[0]]
        content = " ".join(content_parts)

    if not ai_summary:
        meta_result = await db.execute(
            text("SELECT metadata FROM pages WHERE id=:pid"), {"pid": page_id}
        )
        meta_row = meta_result.fetchone()
        if meta_row and meta_row[0]:
            try:
                import json
                meta = json.loads(meta_row[0])
                ai_summary = meta.get("ai_summary", "")
            except Exception:
                pass

    await db.execute(text("DELETE FROM pages_fts WHERE rowid=:rid"), {"rid": page_id})

    await db.execute(
        text("INSERT INTO pages_fts (rowid, title, content, ai_summary) VALUES (:rid, :t, :c, :a)"),
        {"rid": page_id, "t": title, "c": content, "a": ai_summary},
    )
    await db.commit()


async def search_pages(
    db: AsyncSession,
    query: str,
    notebook_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    tag: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    fts_query = segment_chinese(query)

    sql = """
        SELECT
            p.id as page_id,
            p.title as page_title,
            p.notebook_id,
            n.name as notebook_name,
            snippet(pages_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
            fts.rank
        FROM pages_fts fts
        JOIN pages p ON p.id = fts.rowid
        JOIN notebooks n ON n.id = p.notebook_id
        WHERE pages_fts MATCH :q
    """
    params: dict = {"q": fts_query}

    if notebook_id:
        sql += " AND p.notebook_id = :nid"
        params["nid"] = notebook_id

    if date_from:
        sql += " AND p.updated_at >= :df"
        params["df"] = date_from

    if date_to:
        sql += " AND p.updated_at <= :dt"
        params["dt"] = date_to

    if tag:
        sql += " AND p.id IN (SELECT pt.page_id FROM page_tags pt JOIN tags t ON t.id = pt.tag_id WHERE t.name = :tag)"
        params["tag"] = tag

    sql += " ORDER BY fts.rank LIMIT :lim OFFSET :off"
    params["lim"] = limit
    params["off"] = offset

    result = await db.execute(text(sql), params)
    rows = result.fetchall()

    return [
        {
            "page_id": row[0],
            "page_title": row[1],
            "notebook_id": row[2],
            "notebook_name": row[3],
            "snippet": row[4],
            "rank": row[5],
        }
        for row in rows
    ]


async def count_search_results(
    db: AsyncSession,
    query: str,
    notebook_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    tag: str | None = None,
) -> int:
    fts_query = segment_chinese(query)

    sql = """
        SELECT COUNT(*)
        FROM pages_fts fts
        JOIN pages p ON p.id = fts.rowid
        WHERE pages_fts MATCH :q
    """
    params: dict = {"q": fts_query}

    if notebook_id:
        sql += " AND p.notebook_id = :nid"
        params["nid"] = notebook_id

    if date_from:
        sql += " AND p.updated_at >= :df"
        params["df"] = date_from

    if date_to:
        sql += " AND p.updated_at <= :dt"
        params["dt"] = date_to

    if tag:
        sql += " AND p.id IN (SELECT pt.page_id FROM page_tags pt JOIN tags t ON t.id = pt.tag_id WHERE t.name = :tag)"
        params["tag"] = tag

    result = await db.execute(text(sql), params)
    return result.scalar() or 0
