"""
结算相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class SettlementResult(BaseModel):
    """结算结果"""
    creator_achieved: bool
    participant_achieved: bool
    creator_final_weight: float
    participant_final_weight: float
    creator_weight_loss: float
    participant_weight_loss: float


class SettlementResponse(BaseModel):
    """结算响应"""
    id: str
    plan_id: str
    creator_achieved: bool
    participant_achieved: bool
    creator_final_weight: float
    participant_final_weight: float
    creator_weight_loss: float
    participant_weight_loss: float
    creator_amount: float
    participant_amount: float
    platform_fee: float
    notes: Optional[str]
    settlement_date: datetime
    in_arbitration: Optional[bool] = False
    arbitration_fee: Optional[float] = None
    
    class Config:
        from_attributes = True


class SettlementCalculation(BaseModel):
    """结算计算结果"""
    creator_amount: float = Field(..., ge=0.0)
    participant_amount: float = Field(..., ge=0.0)
    platform_fee: float = Field(..., ge=0.0)
    total_bet: float = Field(..., gt=0.0)
    
    @validator('platform_fee')
    def validate_platform_fee(cls, v, values):
        """验证平台手续费不超过总赌金的10%"""
        if 'total_bet' in values:
            max_fee = values['total_bet'] * 0.10
            if v > max_fee:
                raise ValueError(f'platform_fee cannot exceed 10% of total bet: {max_fee}')
        return v
    
    @validator('creator_amount')
    def validate_total_sum(cls, v, values):
        """验证结算金额总和等于双倍赌金"""
        if all(k in values for k in ['participant_amount', 'platform_fee', 'total_bet']):
            total = v + values['participant_amount'] + values['platform_fee']
            expected = values['total_bet']
            if abs(total - expected) > 0.01:  # 允许浮点误差
                raise ValueError(
                    f'Settlement amounts must sum to total bet. '
                    f'Got {total}, expected {expected}'
                )
        return v
