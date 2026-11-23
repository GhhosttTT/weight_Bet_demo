"""
支付 API 路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.payment import (
    BalanceResponse,
    TransactionResponse,
    TransactionStatusResponse,
    ChargeRequest,
    ChargeIntentResponse,
    ChargeIntentRequest,
    SetupIntentResponse,
    WithdrawRequest
)
from app.services.payment_service import PaymentService
from app.services.stripe_payment_service import StripePaymentService
from app.services.stripe_payout_service import StripePayoutService
from app.config import settings
from app.middleware.auth import get_current_user_id
from app.models.user import User

router = APIRouter()


def _validate_payment_method(db: Session, user_id: str, payment_method_id: str) -> None:
    """支付方式必须已绑定到当前用户，避免客户端伪造或复用他人标识。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.payment_method_id or user.payment_method_id != payment_method_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="支付方式未绑定或已失效"
        )


@router.get("/users/{user_id}/balance", response_model=BalanceResponse)
def get_balance(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取账户余额
    
    - **user_id**: 用户 ID
    """
    # 权限验证
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户余额"
        )
    
    balance = PaymentService.get_balance(db, user_id)
    return BalanceResponse.model_validate(balance)


@router.get("/users/{user_id}/transactions", response_model=List[TransactionResponse])
def get_transaction_history(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取交易历史
    
    - **user_id**: 用户 ID
    - **limit**: 返回数量限制 (默认 50)
    - **offset**: 偏移量 (默认 0)
    """
    # 权限验证
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户交易历史"
        )
    
    transactions = PaymentService.get_transaction_history(db, user_id, limit, offset)
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/transactions/{transaction_id}", response_model=TransactionStatusResponse)
def get_transaction_status(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """查询当前用户单笔交易状态，避免客户端把 PaymentSheet 成功误当成已入账。"""
    transaction = PaymentService.get_transaction(db, current_user_id, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="交易不存在")
    return TransactionStatusResponse.model_validate(transaction)


@router.post("/charge")
def charge(
    request: ChargeRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    充值
    
    - **amount**: 充值金额
    - **payment_method_id**: 支付方式 ID
    
    注意: 实际生产环境需要集成 Stripe 等支付网关
    """
    if settings.PAYMENT_PROVIDER.lower() == "stripe":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="真实支付已启用，请使用 /api/payments/charge/intent",
        )
    _validate_payment_method(db, current_user_id, request.payment_method_id)
    return {
        "success": True,
        "message": "充值成功",
        "amount": request.amount,
        "newBalance": PaymentService.charge_funds(db, current_user_id, request.amount).available_balance
    }


@router.post("/charge/intent", response_model=ChargeIntentResponse)
def create_charge_intent(
    request: ChargeIntentRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """创建真实 Stripe PaymentIntent，余额只由 Webhook 入账。"""
    return StripePaymentService.create_charge_intent(
        db, current_user_id, request.amount, idempotency_key=request.idempotency_key
    )


@router.post("/setup-intent", response_model=SetupIntentResponse)
def create_setup_intent(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """创建 Stripe SetupIntent；客户端通过 PaymentSheet 收集卡信息。"""
    return StripePaymentService.create_setup_intent(db, current_user_id)


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """接收 Stripe 回调；此接口不使用用户 JWT，依赖 Stripe 签名验证。"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    return StripePaymentService.handle_webhook(db, payload, signature)


@router.post("/connect/onboarding")
def create_connect_onboarding_link(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """创建 Stripe Connect Express 提现账户认证链接。"""
    return StripePayoutService.create_onboarding_link(db, current_user_id)


@router.post("/withdraw")
def withdraw(
    request: WithdrawRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提现
    
    - **amount**: 提现金额
    - **payment_method_id**: 支付方式 ID
    
    注意: 实际生产环境需要集成 Stripe 等支付网关
    """
    if settings.PAYMENT_PROVIDER.lower() == "stripe":
        return StripePayoutService.create_withdrawal(db, current_user_id, request.amount)
    _validate_payment_method(db, current_user_id, request.payment_method_id)
    result = PaymentService.withdraw_funds(db, current_user_id, request.amount)
    if not result.success:
        code = status.HTTP_404_NOT_FOUND if result.error == "账户不存在" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=result.error)
    return {"success": True, "message": "提现成功", "amount": request.amount, "transaction_id": result.transaction_id}


def _get_owned_withdrawal(db: Session, current_user_id: str, transaction_id: str):
    """只允许交易所有者触发提现恢复操作。"""
    transaction = PaymentService.get_transaction(db, current_user_id, transaction_id)
    if not transaction or transaction.type.value != "withdraw":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提现交易不存在")
    return transaction


@router.post("/withdraw/{transaction_id}/retry")
def retry_withdrawal(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """恢复 Transfer 已成功但 Payout 尚未落库的提现。"""
    _get_owned_withdrawal(db, current_user_id, transaction_id)
    return StripePayoutService.retry_pending_payout(db, transaction_id)


@router.post("/withdraw/{transaction_id}/reconcile")
def reconcile_withdrawal(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """在 Webhook 丢失时查询 Stripe 并同步提现状态。"""
    _get_owned_withdrawal(db, current_user_id, transaction_id)
    return StripePayoutService.reconcile_pending_payout(db, transaction_id)
