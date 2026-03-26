"""
用户服务
"""
import json
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.betting_plan import BettingPlan
from app.models.check_in import CheckIn
from app.models.transaction import Transaction
from app.models.balance import Balance
from app.models.settlement import Settlement
from app.schemas.user import UserUpdate, UserResponse
from app.logger import get_logger

logger = get_logger()


class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_user_profile(db: Session, user_id: str) -> UserResponse:
        """
        获取用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            
        Returns:
            UserResponse: 用户信息
            
        Raises:
            HTTPException: 用户不存在
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found: {}", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse.from_orm(user)
    
    @staticmethod
    def update_user_profile(
        db: Session, 
        user_id: str, 
        current_user_id: str,
        update_data: UserUpdate
    ) -> UserResponse:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 要更新的用户 ID
            current_user_id: 当前登录用户 ID
            update_data: 更新数据
            
        Returns:
            UserResponse: 更新后的用户信息
            
        Raises:
            HTTPException: 用户不存在或无权限
        """
        # 权限验证: 只能更新自己的信息
        if user_id != current_user_id:
            logger.warning("Permission denied: user {} tried to update user {}", current_user_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改其他用户信息"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found: {}", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info("User profile updated: {}", user_id)
        
        return UserResponse.from_orm(user)
    
    @staticmethod
    def bind_payment_method(
        db: Session,
        user_id: str,
        current_user_id: str,
        payment_method_id: str
    ) -> UserResponse:
        """
        绑定支付方式
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            current_user_id: 当前登录用户 ID
            payment_method_id: 支付方式 ID
            
        Returns:
            UserResponse: 更新后的用户信息
            
        Raises:
            HTTPException: 用户不存在或无权限
        """
        # 权限验证
        if user_id != current_user_id:
            logger.warning("Permission denied: user {} tried to bind payment for user {}", current_user_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改其他用户支付方式"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found: {}", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.payment_method_id = payment_method_id
        db.commit()
        db.refresh(user)
        
        logger.info("Payment method bound for user: {}", user_id)
        
        return UserResponse.from_orm(user)

    @staticmethod
    def export_user_data(
        db: Session,
        user_id: str,
        current_user_id: str
    ) -> Dict[str, Any]:
        """
        导出用户所有数据
        
        Args:
            db: 数据库会话
            user_id: 要导出的用户 ID
            current_user_id: 当前登录用户 ID
            
        Returns:
            Dict[str, Any]: 包含所有用户数据的字典
            
        Raises:
            HTTPException: 用户不存在或无权限
        """
        # 权限验证: 只能导出自己的数据
        if user_id != current_user_id:
            logger.warning("Permission denied: user {} tried to export data for user {}", current_user_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限导出其他用户数据"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found: {}", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 收集用户基本信息
        user_data = {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "gender": user.gender.value if user.gender else None,
            "age": user.age,
            "height": user.height,
            "current_weight": user.current_weight,
            "target_weight": user.target_weight,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        
        # 收集余额信息
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        balance_data = None
        if balance:
            balance_data = {
                "available_balance": balance.available_balance,
                "frozen_balance": balance.frozen_balance,
                "updated_at": balance.updated_at.isoformat() if balance.updated_at else None,
            }
        
        # 收集对赌计划 (作为创建者)
        creator_plans = db.query(BettingPlan).filter(BettingPlan.creator_id == user_id).all()
        creator_plans_data = [
            {
                "id": plan.id,
                "role": "creator",
                "status": plan.status.value,
                "bet_amount": plan.bet_amount,
                "start_date": plan.start_date.isoformat() if plan.start_date else None,
                "end_date": plan.end_date.isoformat() if plan.end_date else None,
                "description": plan.description,
                "initial_weight": plan.creator_initial_weight,
                "target_weight": plan.creator_target_weight,
                "target_weight_loss": plan.creator_target_weight_loss,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
            }
            for plan in creator_plans
        ]
        
        # 收集对赌计划 (作为参与者)
        participant_plans = db.query(BettingPlan).filter(BettingPlan.participant_id == user_id).all()
        participant_plans_data = [
            {
                "id": plan.id,
                "role": "participant",
                "status": plan.status.value,
                "bet_amount": plan.bet_amount,
                "start_date": plan.start_date.isoformat() if plan.start_date else None,
                "end_date": plan.end_date.isoformat() if plan.end_date else None,
                "description": plan.description,
                "initial_weight": plan.participant_initial_weight,
                "target_weight": plan.participant_target_weight,
                "target_weight_loss": plan.participant_target_weight_loss,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
            }
            for plan in participant_plans
        ]
        
        # 收集打卡记录
        check_ins = db.query(CheckIn).filter(CheckIn.user_id == user_id).all()
        check_ins_data = [
            {
                "id": check_in.id,
                "plan_id": check_in.plan_id,
                "weight": check_in.weight,
                "check_in_date": check_in.check_in_date.isoformat() if check_in.check_in_date else None,
                "photo_url": check_in.photo_url,
                "note": check_in.note,
                "review_status": check_in.review_status.value,
                "created_at": check_in.created_at.isoformat() if check_in.created_at else None,
            }
            for check_in in check_ins
        ]
        
        # 收集交易记录
        transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
        transactions_data = [
            {
                "id": transaction.id,
                "type": transaction.type.value,
                "amount": transaction.amount,
                "status": transaction.status.value,
                "related_plan_id": transaction.related_plan_id,
                "related_settlement_id": transaction.related_settlement_id,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None,
            }
            for transaction in transactions
        ]
        
        # 收集结算记录 (作为创建者或参与者)
        all_plan_ids = [p.id for p in creator_plans] + [p.id for p in participant_plans]
        settlements = db.query(Settlement).filter(Settlement.plan_id.in_(all_plan_ids)).all() if all_plan_ids else []
        settlements_data = [
            {
                "id": settlement.id,
                "plan_id": settlement.plan_id,
                "creator_achieved": settlement.creator_achieved,
                "participant_achieved": settlement.participant_achieved,
                "creator_final_weight": settlement.creator_final_weight,
                "participant_final_weight": settlement.participant_final_weight,
                "creator_amount": settlement.creator_amount,
                "participant_amount": settlement.participant_amount,
                "platform_fee": settlement.platform_fee,
                "settlement_date": settlement.settlement_date.isoformat() if settlement.settlement_date else None,
            }
            for settlement in settlements
        ]
        
        # 组装完整数据
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user": user_data,
            "balance": balance_data,
            "betting_plans": {
                "as_creator": creator_plans_data,
                "as_participant": participant_plans_data,
            },
            "check_ins": check_ins_data,
            "transactions": transactions_data,
            "settlements": settlements_data,
        }
        
        logger.info("User data exported: {}", user_id)
        
        return export_data
    
    @staticmethod
    def delete_user_account(
        db: Session,
        user_id: str,
        current_user_id: str
    ) -> None:
        """
        删除或匿名化用户账户及所有个人数据
        
        Args:
            db: 数据库会话
            user_id: 要删除的用户 ID
            current_user_id: 当前登录用户 ID
            
        Raises:
            HTTPException: 用户不存在、无权限或有活跃计划
        """
        # 权限验证: 只能删除自己的账户
        if user_id != current_user_id:
            logger.warning("Permission denied: user {} tried to delete user {}", current_user_id, user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除其他用户账户"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found: {}", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查是否有活跃的对赌计划
        active_plans = db.query(BettingPlan).filter(
            ((BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)),
            BettingPlan.status.in_(["pending", "active"])
        ).count()
        
        if active_plans > 0:
            logger.warning("Cannot delete user {}: has {} active plans", user_id, active_plans)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除账户: 存在进行中的对赌计划,请等待计划完成或取消"
            )
        
        # 检查是否有冻结余额
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if balance and balance.frozen_balance > 0:
            logger.warning("Cannot delete user {}: has frozen balance {}", user_id, balance.frozen_balance)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除账户: 存在冻结资金,请等待结算完成"
            )
        
        # 匿名化用户个人信息 (保留数据用于审计和统计)
        user.email = f"deleted_{user_id}@deleted.com"
        user.nickname = f"已删除用户_{user_id[:8]}"
        user.password_hash = "DELETED"
        user.payment_method_id = None
        
        # 删除打卡记录中的敏感信息
        check_ins = db.query(CheckIn).filter(CheckIn.user_id == user_id).all()
        for check_in in check_ins:
            check_in.photo_url = None
            check_in.note = None
        
        # 清空余额 (如果还有可用余额,应该先提现)
        if balance:
            if balance.available_balance > 0:
                logger.warning("User {} has available balance {}, will be cleared", user_id, balance.available_balance)
            balance.available_balance = 0
            balance.frozen_balance = 0
        
        db.commit()
        
        logger.info("User account deleted/anonymized: {}", user_id)
