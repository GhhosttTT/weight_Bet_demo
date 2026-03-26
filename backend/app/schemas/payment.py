"""
支付相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus


class BalanceResponse(BaseModel):
    """余额响应"""
    user_id: str
    available_balance: float
    frozen_balance: float
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """交易响应"""
    id: str
    user_id: str
    type: TransactionType
    amount: float
    status: TransactionStatus
    related_plan_id: Optional[str]
    related_settlement_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChargeRequest(BaseModel):
    """充值请求"""
    amount: float = Field(..., gt=0.0)
    payment_method_id: Optional[str] = Field(None, alias="paymentMethodId")
    
    class Config:
        populate_by_name = True


class WithdrawRequest(BaseModel):
    """提现请求"""
    amount: float = Field(..., gt=0.0)
    payment_method_id: str


class FreezeResult(BaseModel):
    """冻结结果"""
    success: bool
    transaction_id: Optional[str]
    error: Optional[str]


class TransferResult(BaseModel):
    """转账结果"""
    success: bool
    transaction_id: Optional[str]
    error: Optional[str]


class WithdrawResult(BaseModel):
    """提现结果"""
    success: bool
    transaction_id: Optional[str]
    error: Optional[str]


class AbandonResult(BaseModel):
    """放弃计划结果"""
    success: bool
    plan_id: str
    refunded_amount: Optional[float] = None
    winner_id: Optional[str] = None
    loser_id: Optional[str] = None
    transferred_amount: Optional[float] = None
    message: str
