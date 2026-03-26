"""
争议相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.dispute import DisputeStatus


class DisputeCreate(BaseModel):
    """创建争议请求"""
    reason: str = Field(..., min_length=10, max_length=500, description="争议原因")
    description: Optional[str] = Field(None, max_length=2000, description="详细描述")


class DisputeResponse(BaseModel):
    """争议响应"""
    id: str
    settlement_id: str
    user_id: str
    reason: str
    description: Optional[str]
    status: DisputeStatus
    admin_notes: Optional[str]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DisputeUpdate(BaseModel):
    """更新争议状态 (管理员使用)"""
    status: DisputeStatus
    admin_notes: Optional[str] = Field(None, max_length=2000, description="管理员备注")
