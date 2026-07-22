from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.audit_assistant import run_audit

router = APIRouter()


class AuditRequest(BaseModel):
    query: str


@router.post("/chat")
async def audit_chat(req: AuditRequest):
    """AI 审计对话接口"""
    try:
        result = run_audit(req.query)
        return {
            "status": "success",
            "query": result["query"],
            "answer": result["answer"],
            "chart_config": result.get("chart_config"),
            "source": result.get("source", "mock_audit"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审计助手错误: {str(e)}")