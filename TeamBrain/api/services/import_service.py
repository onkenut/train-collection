import json
import re
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Page, Block, Notebook


def parse_markdown_to_blocks(md_text: str) -> list[dict]:
    blocks = []
    lines = md_text.split("\n")
    i = 0
    sort_order = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("### "):
            blocks.append({"type": "heading3", "content": line[4:].strip(), "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif line.startswith("## "):
            blocks.append({"type": "heading2", "content": line[3:].strip(), "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif line.startswith("# "):
            blocks.append({"type": "heading1", "content": line[2:].strip(), "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_content = "\n".join(code_lines)
            block_type = "mermaid" if lang == "mermaid" else "code"
            props = {"language": lang} if lang else {}
            blocks.append({
                "type": block_type, "content": code_content,
                "properties": props, "sort_order": sort_order,
            })
            sort_order += 1
            i += 1
        elif line.startswith("- [x] ") or line.startswith("- [ ] "):
            checked = line.startswith("- [x] ")
            content = line[6:].strip()
            blocks.append({
                "type": "task_list", "content": content,
                "properties": {"checked": checked}, "sort_order": sort_order,
            })
            sort_order += 1
            i += 1
        elif line.startswith("- "):
            blocks.append({"type": "bullet_list", "content": line[2:].strip(), "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif re.match(r"^\d+\.\s", line):
            content = re.sub(r"^\d+\.\s", "", line).strip()
            blocks.append({"type": "ordered_list", "content": content, "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif line.startswith("> "):
            blocks.append({"type": "blockquote", "content": line[2:].strip(), "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif line.strip() == "---":
            blocks.append({"type": "divider", "content": "", "sort_order": sort_order})
            sort_order += 1
            i += 1
        elif line.startswith("$$"):
            math_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("$$"):
                math_lines.append(lines[i])
                i += 1
            blocks.append({
                "type": "math", "content": "\n".join(math_lines),
                "sort_order": sort_order,
            })
            sort_order += 1
            i += 1
        elif line.strip():
            blocks.append({"type": "paragraph", "content": line.strip(), "sort_order": sort_order})
            sort_order += 1
            i += 1
        else:
            i += 1

    return blocks


async def import_markdown(
    db: AsyncSession,
    notebook_id: str,
    files: list[tuple[str, str]],
) -> list[str]:
    now = datetime.now(timezone.utc).isoformat()
    created_page_ids = []

    for filename, content in files:
        lines = content.split("\n")
        title = filename
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        page = Page(
            notebook_id=notebook_id,
            title=title,
            sort_order=len(created_page_ids),
            created_at=now,
            updated_at=now,
        )
        db.add(page)
        await db.flush()
        created_page_ids.append(page.id)

        blocks_data = parse_markdown_to_blocks(content)
        for bd in blocks_data:
            block = Block(
                page_id=page.id,
                type=bd["type"],
                content=bd.get("content", ""),
                properties=json.dumps(bd.get("properties", {})),
                sort_order=bd.get("sort_order", 0),
                created_at=now,
                updated_at=now,
            )
            db.add(block)

    await db.commit()
    return created_page_ids


async def import_notion(db: AsyncSession, notebook_id: str, notion_data: dict) -> list[str]:
    now = datetime.now(timezone.utc).isoformat()
    created_page_ids = []

    pages_data = notion_data.get("pages", [])
    for i, page_data in enumerate(pages_data):
        title = page_data.get("title", "Untitled")
        blocks_raw = page_data.get("blocks", [])

        page = Page(
            notebook_id=notebook_id,
            title=title,
            sort_order=i,
            created_at=now,
            updated_at=now,
        )
        db.add(page)
        await db.flush()
        created_page_ids.append(page.id)

        for j, br in enumerate(blocks_raw):
            block = Block(
                page_id=page.id,
                type=br.get("type", "paragraph"),
                content=br.get("content", ""),
                properties=json.dumps(br.get("properties", {})),
                sort_order=j,
                created_at=now,
                updated_at=now,
            )
            db.add(block)

    await db.commit()
    return created_page_ids
