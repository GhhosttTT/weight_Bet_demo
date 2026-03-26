"""
BettingPlanService: manage betting plans lifecycle
Provides: create_plan, get_plan_details, accept_plan, confirm_plan,
reject_plan, cancel_plan, revoke_plan, get_user_plans
"""
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.betting_plan import BettingPlan, PlanStatus
from app.schemas.betting_plan import CreatePlanRequest, AcceptPlanRequest, PlanResponse
from app.services.payment_service import PaymentService
from app.services.notification_service import NotificationService
from app.logger import get_logger

logger = get_logger()


class BettingPlanService:
    """Service for betting plan operations"""

    @staticmethod
    def create_plan(db: Session, creator_id: str, request: CreatePlanRequest) -> PlanResponse:
        # validate input
        if request.bet_amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="赌金金额必须大于 0")
        if request.end_date <= request.start_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="结束日期必须晚于开始日期")
        duration = (request.end_date - request.start_date).days
        if duration > 365:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="计划时长不能超过 365 天")
        if request.target_weight >= request.initial_weight:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="目标体重必须小于初始体重")

        target_weight_loss = request.initial_weight - request.target_weight

        plan_id = str(uuid.uuid4())
        plan = BettingPlan(
            id=plan_id,
            creator_id=creator_id,
            participant_id=None,
            status=PlanStatus.PENDING,
            bet_amount=request.bet_amount,
            start_date=request.start_date,
            end_date=request.end_date,
            description=request.description,
            creator_initial_weight=request.initial_weight,
            creator_target_weight=request.target_weight,
            creator_target_weight_loss=target_weight_loss,
            pending_double_check=False,
            created_at=datetime.utcnow(),
        )

        # freeze creator funds
        freeze_result = PaymentService.freeze_funds(db, creator_id, plan_id, request.bet_amount)
        if not freeze_result.success:
            logger.warning("Failed to freeze funds for user %s: %s", creator_id, freeze_result.error)
            if "余额不足" in (freeze_result.error or ""):
                raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"余额不足，需要充值 {request.bet_amount} 元")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"资金冻结失败: {freeze_result.error}")

        try:
            db.add(plan)
            db.commit()
            db.refresh(plan)
        except Exception as e:
            try:
                PaymentService.unfreeze_funds(db, creator_id, plan_id)
            except Exception:
                logger.error("Failed to unfreeze funds after DB error for user %s: %s", creator_id, str(e))
            logger.error("DB error when saving plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建计划失败，请稍后重试")

        logger.info("Betting plan created: {} by user {}", plan_id, creator_id)
        return PlanResponse.from_orm(plan)

    @staticmethod
    def get_plan_details(db: Session, plan_id: str) -> PlanResponse:
        # 使用 options 预加载关联的 User 对象，避免 N+1 查询
        from sqlalchemy.orm import joinedload
        
        plan = db.query(BettingPlan).options(
            joinedload(BettingPlan.creator),
            joinedload(BettingPlan.participant)
        ).filter(BettingPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        
        # 构建包含用户信息的响应
        response_data = {
            "id": plan.id,
            "creator_id": plan.creator_id,
            "creator_nickname": plan.creator.nickname if plan.creator else None,
            "creator_email": plan.creator.email if plan.creator else None,
            "participant_id": plan.participant_id,
            "participant_nickname": plan.participant.nickname if plan.participant else None,
            "participant_email": plan.participant.email if plan.participant else None,
            "status": plan.status,
            "bet_amount": plan.bet_amount,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "description": plan.description,
            "creator_initial_weight": plan.creator_initial_weight,
            "creator_target_weight": plan.creator_target_weight,
            "creator_target_weight_loss": plan.creator_target_weight_loss,
            "participant_initial_weight": plan.participant_initial_weight,
            "participant_target_weight": plan.participant_target_weight,
            "participant_target_weight_loss": plan.participant_target_weight_loss,
            "created_at": plan.created_at,
            "activated_at": plan.activated_at
        }
        
        return PlanResponse(**response_data)

    @staticmethod
    def accept_plan(db: Session, plan_id: str, participant_id: str, request: AcceptPlanRequest) -> PlanResponse:
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        if plan.status != PlanStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="计划状态不允许接受")
        if plan.creator_id == participant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能接受自己创建的计划")
        if plan.participant_id is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该计划已被其他用户接受，无法再次接受")

        if request.target_weight >= request.initial_weight:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="目标体重必须小于初始体重")

        target_weight_loss = request.initial_weight - request.target_weight

        # freeze participant funds
        freeze_result = PaymentService.freeze_funds(db, participant_id, plan_id, plan.bet_amount)
        if not freeze_result.success:
            logger.warning("Failed to freeze funds for user %s: %s", participant_id, freeze_result.error)
            if "余额不足" in (freeze_result.error or ""):
                raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"余额不足，需要充值 {plan.bet_amount} 元")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"资金冻结失败: {freeze_result.error}")

        # update plan and set pending_double_check
        plan.participant_id = participant_id
        plan.participant_initial_weight = request.initial_weight
        plan.participant_target_weight = request.target_weight
        plan.participant_target_weight_loss = target_weight_loss
        plan.pending_double_check = True
        plan.status = PlanStatus.WAITING_DOUBLE_CHECK  # 修改为待二次确认状态

        try:
            db.commit()
            db.refresh(plan)
        except Exception as e:
            # rollback: attempt to unfreeze participant funds
            try:
                PaymentService.unfreeze_funds(db, participant_id, plan_id)
            except Exception:
                logger.error("Failed to unfreeze participant funds after DB error for user %s: %s", participant_id, str(e))
            logger.error("DB error when updating plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="接受计划失败，请稍后重试")

        logger.info("Plan %s accepted by participant %s", plan_id, participant_id)

        # best-effort notify creator about pending double-check
        try:
            NotificationService.send_plan_invitation_notification(db, plan.creator_id, plan_id, getattr(plan, 'creator', None))
        except Exception as e:
            logger.error("Failed to notify creator about pending double-check for plan %s: %s", plan_id, str(e))

        return PlanResponse.from_orm(plan)

    @staticmethod
    def confirm_plan(db: Session, plan_id: str, user_id: str) -> PlanResponse:
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        if plan.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有创建者可以确认计划")
        if not plan.participant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参与者未接受计划")
        if plan.status != PlanStatus.WAITING_DOUBLE_CHECK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="计划状态不是待二次确认")
        if not plan.participant_initial_weight or not plan.participant_target_weight:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参与者未设置目标")
        if plan.participant_target_weight >= plan.participant_initial_weight:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参与者的目标体重设置无效")

        # activate plan
        plan.status = PlanStatus.ACTIVE
        plan.activated_at = datetime.utcnow()
        plan.pending_double_check = False

        try:
            db.commit()
            db.refresh(plan)
        except Exception as e:
            logger.error("DB error when confirming plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="确认计划失败，请稍后重试")

        logger.info("Plan %s confirmed by creator %s", plan_id, user_id)

        # notify both parties (best-effort)
        try:
            NotificationService.send_plan_activated_notification(db, plan.creator_id, plan_id)
            if plan.participant_id:
                NotificationService.send_plan_activated_notification(db, plan.participant_id, plan_id)
        except Exception as e:
            logger.error("Failed to send activation notifications for plan %s: %s", plan_id, str(e))

        return PlanResponse.from_orm(plan)

    @staticmethod
    def reject_plan(db: Session, plan_id: str, user_id: str) -> dict:
        """Participant or creator can reject under different conditions.

        - Participant rejecting an invitation: clears participant and unfreezes their funds.
        - Creator rejecting after participant filled targets: cancels the plan and unfreezes both funds.
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")

        # participant rejecting
        if plan.participant_id == user_id:
            # only allowed when plan is pending and awaiting confirmation
            if not plan.pending_double_check:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不能拒绝")
            participant_id = plan.participant_id
            plan.participant_id = None
            plan.participant_initial_weight = None
            plan.participant_target_weight = None
            plan.participant_target_weight_loss = None
            plan.pending_double_check = False

            try:
                db.commit()
                # unfreeze participant funds
                try:
                    PaymentService.unfreeze_funds(db, participant_id, plan_id)
                except Exception:
                    logger.error("Failed to unfreeze participant funds for plan %s, user %s", plan_id, participant_id)
            except Exception as e:
                logger.error("DB error when participant rejecting plan %s: %s", plan_id, str(e))
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="拒绝计划失败，请稍后重试")

            # notify creator
            try:
                NotificationService.send_plan_rejected_notification(db, plan.creator_id, plan_id)
            except Exception:
                logger.exception("Failed to notify creator about participant rejection for plan %s", plan_id)

            logger.info("Plan %s rejected by participant %s", plan_id, user_id)
            return {"result": "rejected"}

        # creator rejecting (cancel after participant accepted)
        if plan.creator_id == user_id:
            # allowed if waiting_double_check or status is PENDING
            if plan.status not in [PlanStatus.PENDING, PlanStatus.WAITING_DOUBLE_CHECK]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能拒绝未生效的计划")

            participant_id = plan.participant_id
            plan.status = PlanStatus.CANCELLED
            plan.participant_id = None
            plan.pending_double_check = False

            try:
                db.commit()
                # unfreeze creator funds
                try:
                    PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
                except Exception:
                    logger.error("Failed to unfreeze creator funds for plan %s, user %s", plan_id, plan.creator_id)
                # unfreeze participant funds if any
                if participant_id:
                    try:
                        PaymentService.unfreeze_funds(db, participant_id, plan_id)
                    except Exception:
                        logger.error("Failed to unfreeze participant funds for plan %s, user %s", plan_id, participant_id)
            except Exception as e:
                logger.error("DB error when creator rejecting plan %s: %s", plan_id, str(e))
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="拒绝计划失败，请稍后重试")

            # notify participant
            if participant_id:
                try:
                    NotificationService.send_plan_rejected_notification(db, participant_id, plan_id)
                except Exception:
                    logger.exception("Failed to notify participant about creator rejection for plan %s", plan_id)

            logger.info("Plan %s rejected/cancelled by creator %s", plan_id, user_id)
            return {"result": "cancelled"}

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权拒绝此计划")

    @staticmethod
    def cancel_plan(db: Session, plan_id: str, user_id: str) -> dict:
        """Only creator can cancel a non-active plan (no funds should be permanently transferred).
        This will unfreeze creator (and participant if present) funds and mark plan CANCELLED.
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        if plan.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有创建者可以取消计划")
        if plan.status == PlanStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能取消未生效的计划")

        participant_id = plan.participant_id
        plan.status = PlanStatus.CANCELLED
        plan.participant_id = None
        plan.pending_double_check = False

        try:
            db.commit()
            # unfreeze creator funds
            try:
                PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
            except Exception:
                logger.error("Failed to unfreeze creator funds for plan %s", plan_id)
            # unfreeze participant funds if any
            if participant_id:
                try:
                    PaymentService.unfreeze_funds(db, participant_id, plan_id)
                except Exception:
                    logger.error("Failed to unfreeze participant funds for plan %s, participant %s", plan_id, participant_id)
        except Exception as e:
            logger.error("DB error when cancelling plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="取消计划失败，请稍后重试")

        logger.info("Plan cancelled: %s by user %s", plan_id, user_id)
        return {"result": "cancelled"}

    @staticmethod
    def revoke_plan(db: Session, plan_id: str, user_id: str) -> dict:
        """Revoke a plan that hasn't been accepted yet. Only creator can revoke.
        This is similar to cancel but intended for plans with no participant.
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        if plan.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有创建者可以撤销计划")
        # 只能撤销未被接受的计划（有待二次确认状态或无参与者）
        if plan.participant_id is not None and plan.status != PlanStatus.WAITING_DOUBLE_CHECK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能撤销未被接受的计划")

        plan.status = PlanStatus.REVOKED if hasattr(PlanStatus, 'REVOKED') else PlanStatus.CANCELLED

        try:
            db.commit()
            # unfreeze creator funds
            try:
                PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
            except Exception:
                logger.error("Failed to unfreeze creator funds for plan %s", plan_id)
        except Exception as e:
            logger.error("DB error when revoking plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="撤销计划失败，请稍后重试")

        logger.info("Plan revoked: %s by user %s", plan_id, user_id)
        return {"result": "revoked"}

    @staticmethod
    def get_user_plans(
        db: Session,
        user_id: str,
        status_filter: Optional[PlanStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PlanResponse]:
        """获取用户的计划列表"""
        query = db.query(BettingPlan).filter(
            (BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)
        )
        if status_filter:
            query = query.filter(BettingPlan.status == status_filter)
        plans = query.order_by(BettingPlan.created_at.desc()).limit(limit).offset(offset).all()
        return [PlanResponse.from_orm(p) for p in plans]
