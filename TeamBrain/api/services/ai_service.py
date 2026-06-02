import hashlib
import json
from typing import Optional

import httpx
from cachetools import TTLCache
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AIUsage, AIRequestLog, Setting

_cache = TTLCache(maxsize=256, ttl=3600)

ACTION_PROMPTS = {
    "continue": (
        "You are a writing assistant. Continue the following text naturally, "
        "maintaining the same style and tone:\n\n{content}"
    ),
    "summarize": (
        "You are a writing assistant. Summarize the following text concisely:\n\n{content}"
    ),
    "rewrite": (
        "You are a writing assistant. Rewrite the following text"
        "{tone_instruction}{rewrite_instruction}:\n\n{content}"
    ),
    "translate": (
        "You are a translation assistant. Translate the following text to {target_lang}:\n\n{content}"
    ),
    "brainstorm": (
        "You are a creative assistant. Based on the following topic, "
        "generate a brainstorm list of ideas:\n\n{content}"
    ),
}


def _build_prompt(action: str, content: str, params: Optional[dict] = None) -> str:
    template = ACTION_PROMPTS.get(action, ACTION_PROMPTS["continue"])
    params = params or {}
    tone_instruction = ""
    rewrite_instruction = ""
    target_lang = params.get("target_lang", "English")

    if params.get("tone") == "formal":
        tone_instruction = " in a formal tone"
    elif params.get("tone") == "casual":
        tone_instruction = " in a casual tone"

    rewrite_type = params.get("rewrite_type", "polish")
    if rewrite_type == "simplify":
        rewrite_instruction = " with simpler language"
    elif rewrite_type == "expand":
        rewrite_instruction = " with more detail and expansion"
    elif rewrite_type == "polish":
        rewrite_instruction = " with polished language"

    return template.format(
        content=content,
        tone_instruction=tone_instruction,
        rewrite_instruction=rewrite_instruction,
        target_lang=target_lang,
    )


def _cache_key(action: str, content: str, params: Optional[dict] = None) -> str:
    raw = f"{action}:{content}:{json.dumps(params or {}, sort_keys=True)}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def get_ai_config(db: AsyncSession) -> dict:
    result = await db.execute(text("SELECT key, value FROM settings WHERE key LIKE 'ai_%'"))
    rows = result.fetchall()
    config = {row[0]: row[1] for row in rows}
    return {
        "api_key": config.get("ai_api_key", ""),
        "base_url": config.get("ai_base_url", "https://api.openai.com/v1"),
        "model": config.get("ai_model", "gpt-3.5-turbo"),
        "monthly_budget": int(config.get("ai_monthly_budget", "1000000")),
    }


async def check_quota(db: AsyncSession, budget_limit: int) -> bool:
    from datetime import datetime
    now = datetime.utcnow()
    result = await db.execute(
        text("SELECT total_tokens FROM ai_usage WHERE month=:m AND year=:y"),
        {"m": now.month, "y": now.year},
    )
    row = result.fetchone()
    current_tokens = row[0] if row else 0
    return current_tokens < budget_limit


async def get_monthly_usage(db: AsyncSession) -> dict:
    from datetime import datetime
    now = datetime.utcnow()
    result = await db.execute(
        text("SELECT total_tokens, budget_limit FROM ai_usage WHERE month=:m AND year=:y"),
        {"m": now.month, "y": now.year},
    )
    row = result.fetchone()
    if row:
        return {"month": now.month, "year": now.year, "total_tokens": row[0], "budget_limit": row[1]}
    budget_result = await db.execute(text("SELECT value FROM settings WHERE key='ai_monthly_budget'"))
    budget_row = budget_result.fetchone()
    budget = int(budget_row[0]) if budget_row else 1000000
    return {"month": now.month, "year": now.year, "total_tokens": 0, "budget_limit": budget}


async def call_llm(api_key: str, base_url: str, model: str, prompt: str) -> tuple[str, int]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    generated = data["choices"][0]["message"]["content"]
    tokens_used = data.get("usage", {}).get("total_tokens", 0)
    return generated, tokens_used


async def track_usage(db: AsyncSession, action: str, tokens_used: int, model: str, cached: bool, prompt_hash: str):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    result = await db.execute(
        text("SELECT id, total_tokens FROM ai_usage WHERE month=:m AND year=:y"),
        {"m": now.month, "y": now.year},
    )
    row = result.fetchone()
    if row:
        usage_id = row[0]
        new_total = row[1] + tokens_used
        await db.execute(
            text("UPDATE ai_usage SET total_tokens=:t, updated_at=:u WHERE id=:id"),
            {"t": new_total, "u": now.isoformat(), "id": usage_id},
        )
    else:
        budget_result = await db.execute(text("SELECT value FROM settings WHERE key='ai_monthly_budget'"))
        budget_row = budget_result.fetchone()
        budget = int(budget_row[0]) if budget_row else 1000000
        usage = AIUsage(
            month=now.month,
            year=now.year,
            total_tokens=tokens_used,
            budget_limit=budget,
            updated_at=now.isoformat(),
        )
        db.add(usage)
        await db.flush()
        usage_id = usage.id

    log = AIRequestLog(
        usage_id=usage_id,
        action=action,
        tokens_used=tokens_used,
        model=model,
        cached=cached,
        prompt_hash=prompt_hash,
        created_at=now.isoformat(),
    )
    db.add(log)
    await db.commit()


async def generate(db: AsyncSession, action: str, content: str, params: Optional[dict] = None) -> dict:
    import uuid

    config = await get_ai_config(db)
    cache_k = _cache_key(action, content, params)

    if cache_k in _cache:
        cached_result = _cache[cache_k]
        await track_usage(db, action, 0, config["model"], True, cache_k)
        return {
            "id": uuid.uuid4().hex,
            "generated_text": cached_result["text"],
            "tokens_used": 0,
            "cached": True,
        }

    if not config["api_key"]:
        raise ValueError("AI API key is not configured")

    budget = int(config.get("monthly_budget", 1000000))
    if not await check_quota(db, budget):
        raise ValueError("Monthly AI token budget exceeded")

    prompt = _build_prompt(action, content, params)
    generated_text, tokens_used = await call_llm(
        config["api_key"], config["base_url"], config["model"], prompt
    )

    _cache[cache_k] = {"text": generated_text}
    await track_usage(db, action, tokens_used, config["model"], False, cache_k)

    return {
        "id": uuid.uuid4().hex,
        "generated_text": generated_text,
        "tokens_used": tokens_used,
        "cached": False,
    }
