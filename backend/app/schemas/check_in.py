"""
打卡记录相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from app.models.check_in import ReviewStatus


class CreateCheckInRequest(BaseModel):
    """创建打卡记录请求"""
    plan_id: str = Field(..., description="计划 ID")
    weight: float = Field(..., ge=30.0, le=300.0, description="体重 (kg)")
    check_in_date: date = Field(..., description="打卡日期")
    photo_url: Optional[str] = Field(None, max_length=500, description="体重秤照片 URL")
    note: Optional[str] = Field(None, max_length=500, description="备注")


class ReviewCheckInRequest(BaseModel):
    """审核打卡记录请求"""
    review_status: ReviewStatus = Field(..., description="审核状态")
    review_comment: Optional[str] = Field(None, max_length=500, description="审核意见")


class CheckInResponse(BaseModel):
    """打卡记录响应"""
    id: str
    user_id: str
    plan_id: str
    weight: float
    check_in_date: date
    photo_url: Optional[str]
    note: Optional[str]
    review_status: ReviewStatus
    reviewer_id: Optional[str]
    review_comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProgressStats(BaseModel):
    """进度统计"""
    current_weight: float = Field(..., description="当前体重")
    initial_weight: float = Field(..., description="初始体重")
    target_weight: float = Field(..., description="目标体重")
    weight_loss: float = Field(..., description="已减重量")
    target_weight_loss: float = Field(..., description="目标减重量")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="进度百分比")
    check_in_count: int = Field(..., ge=0, description="打卡次数")
    days_remaining: int = Field(..., ge=0, description="剩余天数")


class UploadPhotoRequest(BaseModel):
    """上传照片请求"""
    check_in_id: str = Field(..., description="打卡记录 ID")
    photo_url: str = Field(..., max_length=500, description="照片 URL")
