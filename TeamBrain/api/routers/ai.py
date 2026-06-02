from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Setting
from ..schemas import AIRequest, AIResponse, AIUsageOut, AIConfigUpdate, AIConfigOut
from ..services.ai_service import generate, get_ai_config, get_monthly_usage

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/generate", response_model=AIResponse)
async def ai_generate(body: AIRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await generate(db, body.action, body.content, body.params)
        return AIResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.get("/usage", response_model=AIUsageOut)
async def ai_usage(db: AsyncSession = Depends(get_db)):
    usage = await get_monthly_usage(db)
    return AIUsageOut(**usage)


@router.get("/config", response_model=AIConfigOut)
async def get_config(db: AsyncSession = Depends(get_db)):
    config = await get_ai_config(db)
    return AIConfigOut(**config)


@router.put("/config", response_model=AIConfigOut)
async def update_config(body: AIConfigUpdate, db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    mapping = {
        "api_key": "ai_api_key",
        "base_url": "ai_base_url",
        "model": "ai_model",
        "monthly_budget": "ai_monthly_budget",
    }

    for field, key in mapping.items():
        value = getattr(body, field)
        if value is not None:
            result = await db.execute(text("SELECT key FROM settings WHERE key=:k"), {"k": key})
            if result.fetchone():
                await db.execute(
                    text("UPDATE settings SET value=:v, updated_at=:u WHERE key=:k"),
                    {"v": str(value), "u": now, "k": key},
                )
            else:
                db.add(Setting(key=key, value=str(value), updated_at=now))

    await db.commit()
    config = await get_ai_config(db)
    return AIConfigOut(**config)
