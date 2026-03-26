"""
计划状态管理服务
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Optional, List
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.invitation import Invitation, InvitationStatus
from app.logger import get_logger

logger = get_logger()


class InvalidStateTransitionError(Exception):
    """非法状态转换错误"""
    pass


class PlanStatusManager:
    """计划状态管理器"""
    
    # 定义合法的状态转换
    VALID_TRANSITIONS = {
        PlanStatus.PENDING: [PlanStatus.ACTIVE, PlanStatus.REJECTED, PlanStatus.CANCELLED, PlanStatus.EXPIRED],
        PlanStatus.ACTIVE: [PlanStatus.CANCELLED, PlanStatus.COMPLETED, PlanStatus.EXPIRED],
        PlanStatus.COMPLETED: [],  # 已完成状态不能转换
        PlanStatus.CANCELLED: [],  # 已取消状态不能转换
        PlanStatus.REJECTED: [],   # 已拒绝状态不能转换
        PlanStatus.EXPIRED: []     # 已过期状态不能转换
    }
    
    @staticmethod
    def transition_status(
        db: Session,
        plan_id: str,
        from_status: PlanStatus,
        to_status: PlanStatus,
        user_id: Optional[str] = None
    ) -> BettingPlan:
        """
        执行计划状态转换
        
        Args:
            db: 数据库会话
            plan_id: 计划ID
            from_status: 期望的当前状态
            to_status: 目标状态
            user_id: 执行操作的用户ID（可选）
            
        Returns:
            更新后的计划对象
            
        Raises:
            ValueError: 计划不存在或状态不匹配
            InvalidStateTransitionError: 非法的状态转换
        """
        try:
            # 获取计划
            plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
            
            if not plan:
                raise ValueError(f"计划不存在: {plan_id}")
            
            # 验证当前状态
            if plan.status != from_status:
                raise ValueError(
                    f"计划状态不匹配: 期望 {from_status.value}, 实际 {plan.status.value}"
                )
            
            # 验证状态转换合法性
            if to_status not in PlanStatusManager.VALID_TRANSITIONS.get(from_status, []):
                raise InvalidStateTransitionError(
                    f"非法的状态转换: {from_status.value} -> {to_status.value}"
                )
            
            # 执行状态转换
            plan.status = to_status
            
            # 记录状态变更时间戳
            current_time = datetime.now()
            
            if to_status == PlanStatus.ACTIVE:
                plan.activated_at = current_time
            elif to_status == PlanStatus.CANCELLED:
                plan.abandoned_at = current_time
                if user_id:
                    plan.abandoned_by = user_id
            elif to_status == PlanStatus.EXPIRED:
                plan.expiry_checked_at = current_time
            
            db.add(plan)
            db.flush()
            
            logger.info(
                f"状态转换成功: plan_id={plan_id}, "
                f"{from_status.value} -> {to_status.value}, "
                f"user_id={user_id}"
            )
            
            return plan
            
        except (ValueError, InvalidStateTransitionError) as e:
            logger.error(f"状态转换失败: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"数据库错误: {str(e)}")
            raise

    @staticmethod
    def check_expired_plans(db: Session) -> List[BettingPlan]:
        """
        检查并标记过期计划
        
        Args:
            db: 数据库会话
            
        Returns:
            List[BettingPlan]: 过期计划列表
        """
        from app.services.notification_service import NotificationService
        
        expired_plans = []
        current_time = datetime.now()
        
        # 查询所有可能过期的计划
        active_plans = db.query(BettingPlan).filter(
            BettingPlan.status == PlanStatus.ACTIVE,
            BettingPlan.end_date < current_time
        ).all()
        
        for plan in active_plans:
            try:
                # 更新状态
                plan.status = PlanStatus.EXPIRED
                plan.expiry_checked_at = current_time
                db.add(plan)
                db.commit()
                
                # 发送过期通知给创建者
                try:
                    NotificationService.send_plan_expired_notification(
                        db, plan.creator_id, plan.id
                    )
                except Exception as e:
                    logger.error(f"Failed to send expiry notification to creator {plan.creator_id}: {str(e)}")
                
                # 发送过期通知给参与者（如果存在）
                if plan.participant_id:
                    try:
                        NotificationService.send_plan_expired_notification(
                            db, plan.participant_id, plan.id
                        )
                    except Exception as e:
                        logger.error(f"Failed to send expiry notification to participant {plan.participant_id}: {str(e)}")
                
                expired_plans.append(plan)
                
                logger.info(f"Plan marked as expired: plan_id={plan.id}")
                
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Failed to mark plan as expired: plan_id={plan.id}, error={str(e)}")
        
        return expired_plans
    
    @staticmethod
    def mark_as_expired(
        db: Session,
        plan_id: str
    ) -> BettingPlan:
        """
        标记计划为过期
        
        Args:
            db: 数据库会话
            plan_id: 计划ID
            
        Returns:
            BettingPlan: 更新后的计划对象
            
        Raises:
            ValueError: 计划不存在
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        
        if not plan:
            raise ValueError(f"计划不存在: {plan_id}")
        
        plan.status = PlanStatus.EXPIRED
        plan.expiry_checked_at = datetime.now()
        
        db.add(plan)
        db.flush()
        
        logger.info(f"Plan marked as expired: plan_id={plan_id}")
        
        return plan
    
    @staticmethod
    def abandon_plan(
        db: Session,
        plan_id: str,
        user_id: str
    ):
        """
        放弃计划的入口方法
        
        根据计划状态调用相应的放弃逻辑:
        - PENDING: 调用 _abandon_pending_plan
        - ACTIVE: 调用 _abandon_active_plan
        
        Args:
            db: 数据库会话
            plan_id: 计划ID
            user_id: 执行放弃操作的用户ID
            
        Returns:
            AbandonResult: 放弃结果
            
        Raises:
            ValueError: 计划不存在或用户无权限
            InvalidStateTransitionError: 计划状态不允许放弃
        """
        from app.schemas.payment import AbandonResult
        
        # 获取计划
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        
        if not plan:
            logger.warning(f"Plan not found: {plan_id}")
            raise ValueError(f"计划不存在: {plan_id}")
        
        # 验证用户权限
        if plan.status == PlanStatus.PENDING:
            # PENDING 状态只有创建者可以放弃
            if plan.creator_id != user_id:
                logger.warning(
                    f"User {user_id} is not the creator of plan {plan_id}"
                )
                raise ValueError("只有创建者可以放弃待接受状态的计划")
        elif plan.status == PlanStatus.ACTIVE:
            # ACTIVE 状态双方都可以放弃
            if user_id != plan.creator_id and user_id != plan.participant_id:
                logger.warning(
                    f"User {user_id} is not a participant of plan {plan_id}"
                )
                raise ValueError("只有参与者可以放弃进行中的计划")
        else:
            # 其他状态不允许放弃
            logger.warning(
                f"Plan {plan_id} is in {plan.status.value} status, cannot abandon"
            )
            raise InvalidStateTransitionError(
                f"计划状态 {plan.status.value} 不允许放弃"
            )
        
        # 根据计划状态调用相应的放弃逻辑
        if plan.status == PlanStatus.PENDING:
            return PlanStatusManager._abandon_pending_plan(db, plan, user_id)
        else:  # ACTIVE
            return PlanStatusManager._abandon_active_plan(db, plan, user_id)
    
    @staticmethod
    def _abandon_pending_plan(
        db: Session,
        plan: BettingPlan,
        user_id: str
    ):
        """
        放弃待接受状态的计划
        
        Args:
            db: 数据库会话
            plan: 计划对象
            user_id: 用户ID
            
        Returns:
            AbandonResult: 放弃结果
        """
        from app.schemas.payment import AbandonResult
        from app.services.payment_service import PaymentService
        
        try:
            # 开始事务
            # 解冻创建者赌金
            unfreeze_success = PaymentService.unfreeze_funds(
                db, user_id, plan.id
            )
            
            if not unfreeze_success:
                logger.error(f"Failed to unfreeze funds for user {user_id}, plan {plan.id}")
                raise Exception("资金解冻失败")
            
            # 更新计划状态
            plan.status = PlanStatus.CANCELLED
            plan.abandoned_by = user_id
            plan.abandoned_at = datetime.now()
            
            db.add(plan)
            db.flush()
            
            # 更新邀请状态（如果存在）
            invitation = db.query(Invitation).filter(
                Invitation.plan_id == plan.id
            ).first()
            
            if invitation and invitation.invitee_id:
                invitation.status = InvitationStatus.EXPIRED
                db.add(invitation)
            
            # 提交事务
            db.commit()
            
            logger.info(
                f"Pending plan abandoned successfully: plan_id={plan.id}, "
                f"user_id={user_id}, refunded_amount={plan.bet_amount}"
            )
            
            result = AbandonResult(
                success=True,
                plan_id=plan.id,
                refunded_amount=plan.bet_amount,
                message="计划已放弃，赌金已退还"
            )
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to abandon pending plan: {str(e)}")
            raise
    
    @staticmethod
    def _abandon_active_plan(
        db: Session,
        plan: BettingPlan,
        user_id: str
    ):
        """
        放弃进行中的计划
        
        Args:
            db: 数据库会话
            plan: 计划对象
            user_id: 放弃者用户ID
            
        Returns:
            AbandonResult: 放弃结果
        """
        from app.schemas.payment import AbandonResult
        from app.services.payment_service import PaymentService
        
        try:
            # 确定获胜方和失败方
            if user_id == plan.creator_id:
                winner_id = plan.participant_id
                loser_id = plan.creator_id
            else:
                winner_id = plan.creator_id
                loser_id = plan.participant_id
            
            # 解冻双方资金
            unfreeze_loser = PaymentService.unfreeze_funds(db, loser_id, plan.id)
            unfreeze_winner = PaymentService.unfreeze_funds(db, winner_id, plan.id)
            
            if not unfreeze_loser or not unfreeze_winner:
                logger.error(
                    f"Failed to unfreeze funds: loser={unfreeze_loser}, "
                    f"winner={unfreeze_winner}"
                )
                raise Exception("资金解冻失败")
            
            # 转账给获胜方（双倍赌金）
            total_amount = plan.bet_amount * 2
            transfer_result = PaymentService.transfer_funds(
                db, loser_id, winner_id, plan.bet_amount, plan.id
            )
            
            if not transfer_result.success:
                logger.error(
                    f"Failed to transfer funds: {transfer_result.error}"
                )
                raise Exception(f"资金转账失败: {transfer_result.error}")
            
            # 更新计划状态
            plan.status = PlanStatus.CANCELLED
            plan.abandoned_by = user_id
            plan.abandoned_at = datetime.now()
            
            db.add(plan)
            db.flush()
            
            # 提交事务
            db.commit()
            
            logger.info(
                f"Active plan abandoned successfully: plan_id={plan.id}, "
                f"loser_id={loser_id}, winner_id={winner_id}, "
                f"transferred_amount={total_amount}"
            )
            
            result = AbandonResult(
                success=True,
                plan_id=plan.id,
                winner_id=winner_id,
                loser_id=loser_id,
                transferred_amount=total_amount,
                message="计划已放弃，对方获胜"
            )
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to abandon active plan: {str(e)}")
            raise
