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
    amount: float = Field(..., ge=0.01)
    payment_method_id: str = Field(..., min_length=1, alias="paymentMethodId")
    
    class Config:
        populate_by_name = True


class ChargeIntentResponse(BaseModel):
    """真实支付的 PaymentIntent 响应。"""
    transaction_id: str
    payment_intent_id: str
    client_secret: Optional[str]
    amount: float
    status: str


class ChargeIntentRequest(BaseModel):
    """创建 PaymentIntent 的请求；卡信息由 Stripe 客户端组件收集。"""
    amount: float = Field(..., ge=0.01)
    idempotency_key: Optional[str] = Field(default=None, min_length=16, max_length=255, alias="idempotencyKey")

    class Config:
        populate_by_name = True


class WithdrawRequest(BaseModel):
    """提现请求"""
    amount: float = Field(..., ge=0.01)
    # Demo 模式兼容旧支付方式；Stripe 模式使用 Connect 账户，不需要该字段。
    payment_method_id: str = ""


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
