"""后台管理接口数据结构。"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.check_in import ReviewStatus
from app.models.dispute import DisputeStatus


class AdminDisputeUpdate(BaseModel):
    status: DisputeStatus
    admin_notes: Optional[str] = Field(None, max_length=2000)


class AdminCheckInReview(BaseModel):
    review_status: ReviewStatus
    review_comment: Optional[str] = Field(None, max_length=500)


class AdminUserRow(BaseModel):
    id: str
    email: str
    nickname: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
