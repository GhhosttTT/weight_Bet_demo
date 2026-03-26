"""
对赌计划相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.betting_plan import PlanStatus


class AbandonPlanRequest(BaseModel):
    """放弃计划请求"""
    confirmation: bool = Field(..., description="确认放弃标志")


class AbandonPlanResponse(BaseModel):
    """放弃计划响应"""
    success: bool
    plan_id: str
    status: str
    refunded_amount: Optional[float] = None
    transferred_amount: Optional[float] = None
    message: str


class GoalData(BaseModel):
    """目标数据"""
    initial_weight: float = Field(..., ge=30.0, le=300.0)
    target_weight: float = Field(..., ge=30.0, le=300.0)
    target_weight_loss: float = Field(..., gt=0.0)
    
    @validator('target_weight_loss')
    def validate_weight_loss(cls, v, values):
        """验证减重量"""
        if 'initial_weight' in values and 'target_weight' in values:
            expected_loss = values['initial_weight'] - values['target_weight']
            if abs(v - expected_loss) > 0.01:
                raise ValueError('target_weight_loss must equal initial_weight - target_weight')
        return v


class CreatePlanRequest(BaseModel):
    """创建计划请求"""
    bet_amount: float = Field(..., gt=0.0)
    start_date: datetime
    end_date: datetime
    initial_weight: float = Field(..., ge=30.0, le=300.0)
    target_weight: float = Field(..., ge=30.0, le=300.0)
    description: Optional[str] = Field(None, max_length=500)
    invitee_id: Optional[str] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """验证日期"""
        if 'start_date' in values:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
            duration = (v - values['start_date']).days
            if duration > 365:
                raise ValueError('plan duration cannot exceed 365 days')
        return v
    
    @validator('target_weight')
    def validate_weight(cls, v, values):
        """验证目标体重"""
        if 'initial_weight' in values:
            if v >= values['initial_weight']:
                raise ValueError('target_weight must be less than initial_weight')
        return v


class AcceptPlanRequest(BaseModel):
    """接受计划请求"""
    initial_weight: float = Field(..., ge=30.0, le=300.0)
    target_weight: float = Field(..., ge=30.0, le=300.0)
    
    @validator('target_weight')
    def validate_weight(cls, v, values):
        """验证目标体重"""
        if 'initial_weight' in values:
            if v >= values['initial_weight']:
                raise ValueError('target_weight must be less than initial_weight')
        return v


class PlanResponse(BaseModel):
    """计划响应"""
    id: str
    creator_id: str
    creator_nickname: Optional[str] = None
    creator_email: Optional[str] = None
    participant_id: Optional[str]
    participant_nickname: Optional[str] = None
    participant_email: Optional[str] = None
    status: PlanStatus
    bet_amount: float
    start_date: datetime
    end_date: datetime
    description: Optional[str]
    creator_initial_weight: float
    creator_target_weight: float
    creator_target_weight_loss: float
    participant_initial_weight: Optional[float]
    participant_target_weight: Optional[float]
    participant_target_weight_loss: Optional[float]
    created_at: datetime
    activated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
