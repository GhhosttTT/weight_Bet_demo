"""
支付 API 路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.payment import (
    BalanceResponse,
    TransactionResponse,
    ChargeRequest,
    WithdrawRequest
)
from app.services.payment_service import PaymentService
from app.middleware.auth import get_current_user_id

router = APIRouter()


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
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户余额"
        )
    
    balance = PaymentService.get_balance(db, user_id)
    return BalanceResponse.from_orm(balance)


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
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户交易历史"
        )
    
    transactions = PaymentService.get_transaction_history(db, user_id, limit, offset)
    return [TransactionResponse.from_orm(t) for t in transactions]


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
    return {
        "success": True,
        "message": "充值成功",
        "amount": request.amount,
        "newBalance": PaymentService.charge_funds(db, current_user_id, request.amount).available_balance
    }


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
    result = PaymentService.withdraw_funds(db, current_user_id, request.amount)
    if not result.success:
        from fastapi import HTTPException, status
        code = status.HTTP_404_NOT_FOUND if result.error == "账户不存在" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=result.error)
    return {"success": True, "message": "提现成功", "amount": request.amount, "transaction_id": result.transaction_id}
