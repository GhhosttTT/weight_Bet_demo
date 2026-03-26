"""
用户相关的 Pydantic 模式
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import Gender


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    nickname: str = Field(..., min_length=2, max_length=50)
    gender: Gender
    age: int = Field(..., ge=13, le=120)
    height: float = Field(..., ge=100.0, le=250.0)
    current_weight: float = Field(..., ge=30.0, le=300.0)
    target_weight: Optional[float] = Field(None, ge=30.0, le=300.0)


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """用户更新模式"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    height: Optional[float] = Field(None, ge=100.0, le=250.0)
    current_weight: Optional[float] = Field(None, ge=30.0, le=300.0)
    target_weight: Optional[float] = Field(None, ge=30.0, le=300.0)


class UserResponse(UserBase):
    """用户响应模式"""
    id: str
    payment_method_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """用户统计数据"""
    total_plans: int
    active_plans: int
    completed_plans: int
    win_count: int
    loss_count: int
    win_rate: float
    total_weight_loss: float


class UserSearchResult(BaseModel):
    """用户搜索结果模式（只包含公开信息）"""
    user_id: str
    nickname: str
    age: int
    gender: Gender
    
    class Config:
        from_attributes = True
