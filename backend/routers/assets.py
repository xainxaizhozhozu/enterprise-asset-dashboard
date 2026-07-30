from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from database import get_session
from models import Asset, AuditLog, User
from routers.auth import get_current_user, require_role

router = APIRouter()


class AssetCreateRequest(BaseModel):
    name: str
    category: str = "desktop"
    department: str
    owner_id: Optional[int] = None
    purchase_date: Optional[str] = None
    status: str = "active"
    value: Optional[float] = None
    serial_number: Optional[str] = None


class AssetUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = None
    serial_number: Optional[str] = None


def asset_to_dict(asset):
    return {
        "id": asset.id,
        "name": asset.name,
        "category": asset.category,
        "department": asset.department,
        "owner_id": asset.owner_id,
        "purchase_date": str(asset.purchase_date) if asset.purchase_date else None,
        "status": asset.status,
        "value": asset.value,
        "serial_number": asset.serial_number,
        "created_at": str(asset.created_at) if asset.created_at else None,
        "updated_at": str(asset.updated_at) if asset.updated_at else None,
    }


async def _create_audit_log(
    session: AsyncSession,
    user: User,
    action: str,
    resource_id: int,
    details: str,
):
    """写入审计日志"""
    log = AuditLog(
        user_id=user.id,
        action=action,
        resource_type="asset",
        resource_id=resource_id,
        details=details,
    )
    session.add(log)


# 列表查询 — 登录即可
@router.get("/")
async def list_assets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    asset_status: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Asset)
    if category:
        query = query.where(Asset.category == category)
    if asset_status:
        query = query.where(Asset.status == asset_status)
    if department:
        query = query.where(Asset.department == department)
    query = query.order_by(desc(Asset.created_at))
    query = query.offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    assets = result.scalars().all()
    return [asset_to_dict(a) for a in assets]


# 新增资产 — admin / manager
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_asset(
    req: AssetCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin", "manager")),
):
    asset = Asset(
        name=req.name,
        category=req.category,
        department=req.department,
        owner_id=req.owner_id,
        purchase_date=datetime.fromisoformat(req.purchase_date) if req.purchase_date else None,
        status=req.status,
        value=req.value,
        serial_number=req.serial_number,
    )
    session.add(asset)
    await session.flush()

    await _create_audit_log(
        session, current_user, "create", asset.id,
        f"新增资产: {asset.name} (类别={asset.category}, 部门={asset.department})",
    )

    await session.commit()
    await session.refresh(asset)
    return asset_to_dict(asset)


# 查看详情 — 登录即可
@router.get("/{asset_id}")
async def get_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    return asset_to_dict(asset)


# 修改资产 — admin / manager
@router.put("/{asset_id}")
async def update_asset(
    asset_id: int,
    req: AssetUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin", "manager")),
):
    result = await session.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    changed_fields = []
    for key, value in req.model_dump(exclude_unset=True).items():
        if getattr(asset, key) != value:
            changed_fields.append(f"{key}: {getattr(asset, key)} -> {value}")
        setattr(asset, key, value)
    asset.updated_at = datetime.now(timezone.utc)

    detail = f"修改资产 [{asset.name}]: " + "; ".join(changed_fields) if changed_fields else f"修改资产 [{asset.name}] (无变更)"
    await _create_audit_log(session, current_user, "update", asset.id, detail)

    await session.commit()
    await session.refresh(asset)
    return asset_to_dict(asset)


# 删除资产 — 仅 admin
@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    result = await session.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    await _create_audit_log(
        session, current_user, "delete", asset.id,
        f"删除资产: {asset.name} (序列号={asset.serial_number})",
    )

    await session.delete(asset)
    await session.commit()
