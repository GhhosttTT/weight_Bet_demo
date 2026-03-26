"""
支付服务
"""
import uuid
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.schemas.payment import FreezeResult, TransferResult, WithdrawResult
from app.logger import get_logger

logger = get_logger()


class PaymentService:
    """支付服务类"""
    
    @staticmethod
    def _retry_with_exponential_backoff(
        func,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0
    ):
        """
        使用指数退避策略重试函数
        
        Args:
            func: 要重试的函数
            max_retries: 最大重试次数
            initial_delay: 初始延迟时间(秒)
            max_delay: 最大延迟时间(秒)
            
        Returns:
            函数执行结果
            
        Raises:
            最后一次重试的异常
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                logger.warning(
                    "Payment operation failed (attempt {}/{}): {}",
                    attempt + 1, max_retries, str(e),
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "delay": delay
                    }
                )
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    # 指数退避: 每次延迟时间翻倍,但不超过最大延迟
                    delay = min(delay * 2, max_delay)
        
        # 所有重试都失败,记录错误并抛出异常
        logger.error(
            "Payment operation failed after {} attempts: {}",
            max_retries, str(last_exception),
            extra={"max_retries": max_retries},
            exc_info=True
        )
        raise last_exception
    
    @staticmethod
    def freeze_funds(
        db: Session,
        user_id: str,
        plan_id: str,
        amount: float
    ) -> FreezeResult:
        """
        冻结用户资金 (带重试机制)
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            plan_id: 计划 ID
            amount: 冻结金额
            
        Returns:
            FreezeResult: 冻结结果
        """
        def _freeze():
            try:
                # 获取用户余额
                balance = db.query(Balance).filter(Balance.user_id == user_id).first()
                if not balance:
                    logger.warning("Balance not found for user: {}", user_id)
                    return FreezeResult(success=False, transaction_id=None, error="账户余额不存在")
                
                # 检查余额是否充足
                if balance.available_balance < amount:
                    logger.warning("Insufficient balance for user {}: {} < {}", user_id, balance.available_balance, amount)
                    return FreezeResult(success=False, transaction_id=None, error="余额不足")
                
                # 冻结资金
                balance.available_balance -= amount
                balance.frozen_balance += amount
                
                # 创建交易记录
                transaction_id = str(uuid.uuid4())
                transaction = Transaction(
                    id=transaction_id,
                    user_id=user_id,
                    type=TransactionType.FREEZE,
                    amount=amount,
                    status=TransactionStatus.COMPLETED,
                    related_plan_id=plan_id,
                    completed_at=datetime.utcnow()
                )
                db.add(transaction)
                
                db.commit()
                
                logger.info("Funds frozen successfully: user={}, amount={}, plan={}", user_id, amount, plan_id)
                
                return FreezeResult(success=True, transaction_id=transaction_id, error=None)
                
            except Exception as e:
                db.rollback()
                logger.error("Failed to freeze funds: {}", str(e))
                raise
        
        # 使用重试机制执行冻结操作
        try:
            return PaymentService._retry_with_exponential_backoff(_freeze)
        except Exception as e:
            return FreezeResult(success=False, transaction_id=None, error="冻结资金失败: {}".format(str(e)))
    
    @staticmethod
    def unfreeze_funds(
        db: Session,
        user_id: str,
        plan_id: str
    ) -> bool:
        """
        解冻用户资金 (带重试机制)
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            plan_id: 计划 ID
            
        Returns:
            bool: 是否成功
        """
        def _unfreeze():
            try:
                # 获取冻结交易记录
                freeze_transaction = db.query(Transaction).filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.related_plan_id == plan_id,
                        Transaction.type == TransactionType.FREEZE,
                        Transaction.status == TransactionStatus.COMPLETED
                    )
                ).first()
                
                if not freeze_transaction:
                    logger.warning("Freeze transaction not found: user={}, plan={}", user_id, plan_id)
                    return False
                
                amount = freeze_transaction.amount
                
                # 获取用户余额
                balance = db.query(Balance).filter(Balance.user_id == user_id).first()
                if not balance:
                    logger.warning("Balance not found for user: {}", user_id)
                    return False
                
                # 解冻资金
                balance.frozen_balance -= amount
                balance.available_balance += amount
                
                # 创建交易记录
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    type=TransactionType.UNFREEZE,
                    amount=amount,
                    status=TransactionStatus.COMPLETED,
                    related_plan_id=plan_id,
                    completed_at=datetime.utcnow()
                )
                db.add(transaction)
                
                db.commit()
                
                logger.info("Funds unfrozen successfully: user={}, amount={}, plan={}", user_id, amount, plan_id)
                
                return True
                
            except Exception as e:
                db.rollback()
                logger.error("Failed to unfreeze funds: {}", str(e))
                raise
        
        # 使用重试机制执行解冻操作
        try:
            return PaymentService._retry_with_exponential_backoff(_unfreeze)
        except Exception as e:
            logger.error("Unfreeze failed after retries: {}", str(e))
            return False
    
    @staticmethod
    def transfer_funds(
        db: Session,
        from_user_id: str,
        to_user_id: str,
        amount: float,
        plan_id: str = None
    ) -> TransferResult:
        """
        转账 (带重试机制)
        
        Args:
            db: 数据库会话
            from_user_id: 付款方用户 ID
            to_user_id: 收款方用户 ID
            amount: 转账金额
            plan_id: 关联计划 ID (可选)
            
        Returns:
            TransferResult: 转账结果
        """
        def _transfer():
            try:
                # 获取付款方余额
                from_balance = db.query(Balance).filter(Balance.user_id == from_user_id).first()
                if not from_balance:
                    return TransferResult(success=False, transaction_id=None, error="付款方账户不存在")
                
                # 检查余额
                if from_balance.available_balance < amount:
                    return TransferResult(success=False, transaction_id=None, error="付款方余额不足")
                
                # 获取收款方余额
                to_balance = db.query(Balance).filter(Balance.user_id == to_user_id).first()
                if not to_balance:
                    return TransferResult(success=False, transaction_id=None, error="收款方账户不存在")
                
                # 执行转账
                from_balance.available_balance -= amount
                to_balance.available_balance += amount
                
                # 创建交易记录
                transaction_id = str(uuid.uuid4())
                transaction = Transaction(
                    id=transaction_id,
                    user_id=from_user_id,
                    type=TransactionType.TRANSFER,
                    amount=-amount,  # 负数表示支出
                    status=TransactionStatus.COMPLETED,
                    related_plan_id=plan_id,
                    completed_at=datetime.utcnow()
                )
                db.add(transaction)
                
                # 收款方交易记录
                transaction_to = Transaction(
                    id=str(uuid.uuid4()),
                    user_id=to_user_id,
                    type=TransactionType.TRANSFER,
                    amount=amount,  # 正数表示收入
                    status=TransactionStatus.COMPLETED,
                    related_plan_id=plan_id,
                    completed_at=datetime.utcnow()
                )
                db.add(transaction_to)
                
                db.commit()
                
                logger.info("Transfer successful: from={}, to={}, amount={}", from_user_id, to_user_id, amount)
                
                return TransferResult(success=True, transaction_id=transaction_id, error=None)
                
            except Exception as e:
                db.rollback()
                logger.error("Transfer failed: {}", str(e))
                raise
        
        # 使用重试机制执行转账操作
        try:
            return PaymentService._retry_with_exponential_backoff(_transfer)
        except Exception as e:
            return TransferResult(success=False, transaction_id=None, error="转账失败: {}".format(str(e)))
    
    @staticmethod
    def get_balance(db: Session, user_id: str) -> Balance:
        """
        获取账户余额
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            
        Returns:
            Balance: 账户余额
            
        Raises:
            HTTPException: 账户不存在
        """
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if not balance:
            logger.warning("Balance not found for user: {}", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="账户余额不存在"
            )
        
        return balance
    
    @staticmethod
    def get_transaction_history(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ):
        """
        获取交易历史
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Transaction]: 交易记录列表
        """
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(
            Transaction.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return transactions
