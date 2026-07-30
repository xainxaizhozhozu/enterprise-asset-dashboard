from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_session
from models import AuditLog, User
from schemas import AuditRequest
from routers.auth import get_current_user, require_role
from services.audit_assistant import run_audit

router = APIRouter()


@router.post("/chat")
async def audit_chat(
    req: AuditRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """AI 审计对话接口 — 需登录"""
    try:
        result = await run_audit(req.query, session)
        return {
            "status": "success",
            "query": result["query"],
            "answer": result["answer"],
            "chart_config": result.get("chart_config"),
            "source": result.get("source", "mock_audit"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审计助手错误: {str(e)}")


@router.get("/logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    """查看审计日志 — 仅管理员"""
    query = select(AuditLog).order_by(desc(AuditLog.created_at))
    if action:
        query = query.where(AuditLog.action == action)
    query = query.offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "created_at": str(log.created_at) if log.created_at else None,
        }
        for log in logs
    ]
