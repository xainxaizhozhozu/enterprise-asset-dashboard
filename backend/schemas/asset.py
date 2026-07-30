from pydantic import BaseModel
from typing import Optional


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
