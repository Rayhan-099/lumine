from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.api import deps
from app.models.user import User
from app.services.llm import get_llm_provider
from app.models.scan import Scan
from sqlalchemy import select

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    scan_id: str = None  # Optional context


@router.post("")
async def chat_with_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Chat with the AI assistant."""
    scan_context = {}

    if request.scan_id:
        from sqlalchemy.orm import selectinload

        stmt = (
            select(Scan)
            .options(selectinload(Scan.predictions))
            .where(Scan.id == request.scan_id)
        )
        result = await db.execute(stmt)
        scan = result.scalar_one_or_none()

        if scan and scan.predictions:
            pred = scan.predictions[0]
            scan_context = {
                "condition": pred.condition,
                "severity": pred.severity,
                "confidence": pred.confidence,
            }

    llm = get_llm_provider()
    response_text = await llm.chat(request.message, scan_context)

    return {"reply": response_text}
