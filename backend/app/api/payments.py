"""
支付 API 路由
"""
from fastapi import APIRouter, Depends
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
    limit: int = 50,
    offset: int = 0,
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
    # TODO: 集成 Stripe 支付网关
    # 这里简化处理,直接增加余额
    from app.models.balance import Balance
    from app.models.transaction import Transaction, TransactionType, TransactionStatus
    from app.logger import get_logger
    import uuid
    from datetime import datetime
    
    logger = get_logger()
    
    balance = db.query(Balance).filter(Balance.user_id == current_user_id).first()
    if not balance:
        logger.warning(f"Account not found for user: {current_user_id}")
        return {"success": False, "message": "账户不存在"}
    
    # Log old balance
    old_balance = balance.available_balance
    logger.info(f"Charge initiated: user={current_user_id}, amount={request.amount}, old_balance={old_balance}")
    
    # Update balance
    new_balance = old_balance + request.amount
    balance.available_balance = new_balance
    balance.updated_at = datetime.utcnow()
    
    # Create transaction record
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        type=TransactionType.CHARGE,
        amount=request.amount,
        status=TransactionStatus.COMPLETED,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)
    
    # Explicitly add balance to session to ensure tracking
    db.add(balance)
    
    # Flush changes to database before commit
    db.flush()
    
    # Commit transaction
    db.commit()
    
    # Refresh balance to get latest state from database
    db.refresh(balance)
    
    # Log new balance
    logger.info(f"Charge completed: user={current_user_id}, amount={request.amount}, old_balance={old_balance}, new_balance={balance.available_balance}")
    
    return {
        "success": True,
        "message": "充值成功",
        "amount": request.amount,
        "newBalance": balance.available_balance
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
    from app.models.balance import Balance
    from app.models.transaction import Transaction, TransactionType, TransactionStatus
    from fastapi import HTTPException, status
    import uuid
    from datetime import datetime
    
    balance = db.query(Balance).filter(Balance.user_id == current_user_id).first()
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在"
        )
    
    if balance.available_balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足"
        )
    
    # TODO: 集成 Stripe 支付网关
    # 这里简化处理,直接减少余额
    balance.available_balance -= request.amount
    
    # 创建交易记录
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        type=TransactionType.WITHDRAW,
        amount=-request.amount,
        status=TransactionStatus.COMPLETED,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    
    return {"success": True, "message": "提现成功", "amount": request.amount}
