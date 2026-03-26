"""
结算选择相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class SettlementChoiceEnum(str, Enum):
    """结算选择枚举"""
    SELF_ACHIEVED_OPPONENT_NOT = "self_achieved_opponent_not"  # 我达成，对方未达成
    SELF_NOT_OPPONENT_ACHIEVED = "self_not_opponent_achieved"  # 我未达成，对方达成
    BOTH_ACHIEVED = "both_achieved"  # 双方都达成
    BOTH_NOT_ACHIEVED = "both_not_achieved"  # 双方都未达成


class SettlementChoiceRequest(BaseModel):
    """提交结算选择请求"""
    self_achieved: bool = Field(..., description="自己是否达成目标")
    opponent_achieved: bool = Field(..., description="对方是否达成目标")
    
    @validator('self_achieved')
    def validate_self_achieved(cls, v):
        if not isinstance(v, bool):
            raise ValueError("self_achieved 必须是布尔值")
        return v
    
    @validator('opponent_achieved')
    def validate_opponent_achieved(cls, v):
        if not isinstance(v, bool):
            raise ValueError("opponent_achieved 必须是布尔值")
        return v


class SettlementChoiceResponse(BaseModel):
    """结算选择响应"""
    id: str
    plan_id: str
    user_id: str
    self_achieved: bool
    opponent_achieved: bool
    round: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SettlementSelectionStatus(BaseModel):
    """结算选择状态"""
    plan_id: str
    current_round: int = Field(..., ge=1, le=3)
    creator_submitted: bool = False
    participant_submitted: bool = False
    creator_choice: Optional[SettlementChoiceResponse] = None
    participant_choice: Optional[SettlementChoiceResponse] = None
    matched: bool = False
    settlement_completed: bool = False
    in_arbitration: bool = False


class SettlementMatchingResult(BaseModel):
    """结算匹配结果"""
    matched: bool
    creator_won: Optional[bool] = None
    both_achieved: Optional[bool] = None
    both_failed: Optional[bool] = None
    go_to_next_round: bool = False
    go_to_arbitration: bool = False
    message: str


class PlanSettlementInfo(BaseModel):
    """计划结算信息（用于检查结算日弹窗）"""
    plan_id: str = Field(..., description="计划 ID")
    description: str = Field(..., description="计划描述")
    end_date: datetime = Field(..., description="结束日期")
    bet_amount: float = Field(..., description="赌金金额")
    has_settlement: bool = Field(default=False, description="是否已有结算记录")
    in_progress: bool = Field(default=False, description="结算流程是否正在进行中")
