"""
资金管理器服务
处理资金冻结、解冻和转账操作
"""
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.schemas.payment import FreezeResult, TransferResult, AbandonResult
from app.logger import get_logger

logger = get_logger()


class FundManager:
    """资金管理器类"""
    
    @staticmethod
    def freeze_funds(
        db: Session,
        user_id: str,
        plan_id: str,
        amount: float
    ) -> FreezeResult:
        """
        冻结用户资金
        
        验证余额充足性、执行原子性冻结操作、创建交易记录
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            plan_id: 计划 ID
            amount: 冻结金额
            
        Returns:
            FreezeResult: 冻结结果
            
        Validates: Requirements 7.1, 7.2, 7.3, 12.4
        """
        try:
            # 步骤 1: 获取用户余额
            balance = db.query(Balance).filter(Balance.user_id == user_id).first()
            if not balance:
                logger.warning("Balance not found for user: {}", user_id)
                return FreezeResult(
                    success=False,
                    transaction_id=None,
                    error="账户余额不存在"
                )
            
            # 步骤 2: 验证余额充足性 (Requirement 12.4)
            if balance.available_balance < amount:
                logger.warning(
                    "Insufficient balance for user {}: {} < {}",
                    user_id,
                    balance.available_balance,
                    amount
                )
                return FreezeResult(
                    success=False,
                    transaction_id=None,
                    error="余额不足"
                )
            
            # 步骤 3: 执行原子性冻结操作 (Requirement 7.1, 7.2)
            balance.available_balance -= amount
            balance.frozen_balance += amount
            
            # 步骤 4: 创建交易记录 (Requirement 7.3)
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                id=transaction_id,
                user_id=user_id,
                type=TransactionType.FREEZE,
                amount=amount,
                status=TransactionStatus.COMPLETED,
                related_plan_id=plan_id,
                completed_at=datetime.now(timezone.utc)
            )
            db.add(transaction)
            
            # 提交事务
            db.commit()
            
            logger.info(
                "Funds frozen successfully: user={}, amount={}, plan={}",
                user_id,
                amount,
                plan_id
            )
            
            return FreezeResult(
                success=True,
                transaction_id=transaction_id,
                error=None
            )
            
        except Exception as e:
            # 回滚事务 (Requirement 7.2)
            db.rollback()
            logger.error(
                "Failed to freeze funds: {}",
                str(e),
                exc_info=True
            )
            return FreezeResult(
                success=False,
                transaction_id=None,
                error=f"冻结资金失败: {str(e)}"
            )

    @staticmethod
    def unfreeze_funds(
        db: Session,
        user_id: str,
        plan_id: str
    ) -> FreezeResult:
        """
        解冻用户资金
        
        执行原子性解冻操作、创建交易记录
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            plan_id: 计划 ID
            
        Returns:
            FreezeResult: 解冻结果
            
        Validates: Requirements 5.2, 5.4, 7.1, 7.2, 7.3
        """
        try:
            # 步骤 1: 获取用户余额
            balance = db.query(Balance).filter(Balance.user_id == user_id).first()
            if not balance:
                logger.warning("Balance not found for user: {}", user_id)
                return FreezeResult(
                    success=False,
                    transaction_id=None,
                    error="账户余额不存在"
                )
            
            # 步骤 2: 查找冻结交易记录以获取金额
            freeze_transaction = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.related_plan_id == plan_id,
                Transaction.type == TransactionType.FREEZE,
                Transaction.status == TransactionStatus.COMPLETED
            ).first()
            
            if not freeze_transaction:
                logger.warning(
                    "No freeze transaction found for user {} and plan {}",
                    user_id,
                    plan_id
                )
                return FreezeResult(
                    success=False,
                    transaction_id=None,
                    error="未找到冻结记录"
                )
            
            amount = freeze_transaction.amount
            
            # 步骤 3: 验证冻结余额充足性
            if balance.frozen_balance < amount:
                logger.warning(
                    "Insufficient frozen balance for user {}: {} < {}",
                    user_id,
                    balance.frozen_balance,
                    amount
                )
                return FreezeResult(
                    success=False,
                    transaction_id=None,
                    error="冻结余额不足"
                )
            
            # 步骤 4: 执行原子性解冻操作 (Requirement 7.1, 7.2)
            balance.frozen_balance -= amount
            balance.available_balance += amount
            
            # 步骤 5: 创建交易记录 (Requirement 7.3)
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                id=transaction_id,
                user_id=user_id,
                type=TransactionType.UNFREEZE,
                amount=amount,
                status=TransactionStatus.COMPLETED,
                related_plan_id=plan_id,
                completed_at=datetime.now(timezone.utc)
            )
            db.add(transaction)
            
            # 提交事务
            db.commit()
            
            logger.info(
                "Funds unfrozen successfully: user={}, amount={}, plan={}",
                user_id,
                amount,
                plan_id
            )
            
            return FreezeResult(
                success=True,
                transaction_id=transaction_id,
                error=None
            )
            
        except Exception as e:
            # 回滚事务 (Requirement 7.2)
            db.rollback()
            logger.error(
                "Failed to unfreeze funds: {}",
                str(e),
                exc_info=True
            )
            return FreezeResult(
                success=False,
                transaction_id=None,
                error=f"解冻资金失败: {str(e)}"
            )
    
    @staticmethod
    def transfer_funds(
        db: Session,
        from_user_id: str,
        to_user_id: str,
        amount: float,
        plan_id: str
    ) -> TransferResult:
        """
        转账资金
        
        执行原子性转账操作、创建交易记录
        
        Args:
            db: 数据库会话
            from_user_id: 转出用户 ID (可以是 "platform" 表示平台账户)
            to_user_id: 转入用户 ID
            amount: 转账金额
            plan_id: 计划 ID
            
        Returns:
            TransferResult: 转账结果
            
        Validates: Requirements 6.3, 6.4, 7.1, 7.2, 7.3
        """
        try:
            # 步骤 1: 获取转入用户余额
            to_balance = db.query(Balance).filter(Balance.user_id == to_user_id).first()
            if not to_balance:
                logger.warning("Balance not found for recipient: {}", to_user_id)
                return TransferResult(
                    success=False,
                    transaction_id=None,
                    error="收款账户余额不存在"
                )
            
            # 步骤 2: 如果不是平台转账，验证转出用户余额
            if from_user_id != "platform":
                from_balance = db.query(Balance).filter(Balance.user_id == from_user_id).first()
                if not from_balance:
                    logger.warning("Balance not found for sender: {}", from_user_id)
                    return TransferResult(
                        success=False,
                        transaction_id=None,
                        error="付款账户余额不存在"
                    )
                
                if from_balance.available_balance < amount:
                    logger.warning(
                        "Insufficient balance for sender {}: {} < {}",
                        from_user_id,
                        from_balance.available_balance,
                        amount
                    )
                    return TransferResult(
                        success=False,
                        transaction_id=None,
                        error="付款账户余额不足"
                    )
                
                # 扣除转出用户余额
                from_balance.available_balance -= amount
            
            # 步骤 3: 执行原子性转账操作 (Requirement 7.1, 7.2)
            to_balance.available_balance += amount
            
            # 步骤 4: 创建交易记录 (Requirement 7.3)
            transaction_id = str(uuid.uuid4())
            transaction = Transaction(
                id=transaction_id,
                user_id=to_user_id,
                type=TransactionType.TRANSFER,
                amount=amount,
                status=TransactionStatus.COMPLETED,
                related_plan_id=plan_id,
                completed_at=datetime.now(timezone.utc)
            )
            db.add(transaction)
            
            # 提交事务
            db.commit()
            
            logger.info(
                "Funds transferred successfully: from={}, to={}, amount={}, plan={}",
                from_user_id,
                to_user_id,
                amount,
                plan_id
            )
            
            return TransferResult(
                success=True,
                transaction_id=transaction_id,
                error=None
            )
            
        except Exception as e:
            # 回滚事务 (Requirement 7.2)
            db.rollback()
            logger.error(
                "Failed to transfer funds: {}",
                str(e),
                exc_info=True
            )
            return TransferResult(
                success=False,
                transaction_id=None,
                error=f"转账失败: {str(e)}"
            )
    
    @staticmethod
    def process_abandon_refund(
        db: Session,
        plan,
        abandoning_user_id: str
    ) -> AbandonResult:
        """
        处理放弃计划的资金退还逻辑
        
        根据计划状态处理退款逻辑:
        - pending 状态：解冻创建者资金
        - active 状态：转账给获胜方
        使用数据库事务确保原子性
        
        Args:
            db: 数据库会话
            plan: 计划对象
            abandoning_user_id: 放弃计划的用户 ID
            
        Returns:
            AbandonResult: 放弃结果
            
        Validates: Requirements 5.2, 6.3, 6.4, 7.1, 7.2, 7.4
        """
        from app.models.betting_plan import PlanStatus
        
        try:
            # 步骤 1: 根据计划状态处理
            if plan.status == PlanStatus.PENDING:
                # Pending 状态：解冻创建者资金 (Requirement 5.2)
                unfreeze_result = FundManager.unfreeze_funds(
                    db,
                    plan.creator_id,
                    plan.id
                )
                
                if not unfreeze_result.success:
                    return AbandonResult(
                        success=False,
                        plan_id=plan.id,
                        message=f"解冻资金失败: {unfreeze_result.error}"
                    )
                
                logger.info(
                    "Pending plan abandoned, funds unfrozen: plan={}, user={}",
                    plan.id,
                    abandoning_user_id
                )
                
                return AbandonResult(
                    success=True,
                    plan_id=plan.id,
                    refunded_amount=plan.bet_amount,
                    message="计划已放弃，赌金已退还"
                )
                
            elif plan.status == PlanStatus.ACTIVE:
                # Active 状态：转账给获胜方 (Requirement 6.3, 6.4)
                
                # 确定获胜方和失败方
                if abandoning_user_id == plan.creator_id:
                    winner_id = plan.participant_id
                    loser_id = plan.creator_id
                else:
                    winner_id = plan.creator_id
                    loser_id = plan.participant_id
                
                # 只解冻获胜方资金（失败方的资金将被转走）
                unfreeze_winner = FundManager.unfreeze_funds(db, winner_id, plan.id)
                
                if not unfreeze_winner.success:
                    return AbandonResult(
                        success=False,
                        plan_id=plan.id,
                        message="解冻资金失败"
                    )
                
                # 从失败方账户扣除冻结资金（不解冻，直接扣除）
                loser_balance = db.query(Balance).filter(Balance.user_id == loser_id).first()
                if loser_balance and loser_balance.frozen_balance >= plan.bet_amount:
                    loser_balance.frozen_balance -= plan.bet_amount
                
                # 转账给获胜方（双倍赌金）
                total_amount = plan.bet_amount * 2
                transfer_result = FundManager.transfer_funds(
                    db,
                    "platform",
                    winner_id,
                    total_amount,
                    plan.id
                )
                
                if not transfer_result.success:
                    return AbandonResult(
                        success=False,
                        plan_id=plan.id,
                        message=f"转账失败: {transfer_result.error}"
                    )
                
                logger.info(
                    "Active plan abandoned, funds transferred to winner: plan={}, winner={}, amount={}",
                    plan.id,
                    winner_id,
                    total_amount
                )
                
                return AbandonResult(
                    success=True,
                    plan_id=plan.id,
                    winner_id=winner_id,
                    loser_id=loser_id,
                    transferred_amount=total_amount,
                    message="计划已放弃，对方获胜"
                )
            
            else:
                return AbandonResult(
                    success=False,
                    plan_id=plan.id,
                    message=f"计划状态不允许放弃: {plan.status}"
                )
                
        except Exception as e:
            # 回滚事务 (Requirement 7.2)
            db.rollback()
            logger.error(
                "Failed to process abandon refund: {}",
                str(e),
                exc_info=True
            )
            return AbandonResult(
                success=False,
                plan_id=plan.id,
                message=f"处理退款失败: {str(e)}"
            )
