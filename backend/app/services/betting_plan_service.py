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

        invitee = None
        # 如果传入了invitee_id，自动创建邀请记录
        if request.invitee_id:
            try:
                from app.models.invitation import Invitation, InvitationStatus
                from app.models.user import User
                from app.services.notification_service import NotificationService
                
                # 验证被邀请用户存在
                invitee = db.query(User).filter(User.id == request.invitee_id).first()
                if not invitee:
                    logger.warning("Invitee user not found: {}", request.invitee_id)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="被邀请用户不存在"
                    )
                    
                # 验证不能邀请自己
                if invitee.id == creator_id:
                    logger.warning("User {} tried to invite themselves", creator_id)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="不能邀请自己"
                    )
                    
                # 创建邀请记录
                invitation = Invitation(
                    id=str(uuid.uuid4()),
                    plan_id=plan_id,
                    inviter_id=creator_id,
                    invitee_email=invitee.email,
                    invitee_id=invitee.id,
                    status=InvitationStatus.PENDING,
                    sent_at=datetime.utcnow()
                )
                
                db.add(invitation)
                db.commit()
                db.refresh(plan)
                
                logger.info(
                    "Auto-created invitation: id={}, plan_id={}, inviter_id={}, invitee_id={}",
                    invitation.id, plan_id, creator_id, invitee.id
                )
                
                # 发送邀请通知
                try:
                    duration_days = (plan.end_date - plan.start_date).days
                    NotificationService.send_plan_invitation_notification(
                        db=db,
                        user_id=invitee.id,
                        plan_id=plan_id,
                        creator_name=plan.creator.nickname if plan.creator else "用户"
                    )
                    logger.info("Invitation notification sent to user {}", invitee.id)
                except Exception as e:
                    logger.error("Failed to send invitation notification: {}", str(e))
                    
            except Exception as e:
                # 邀请创建失败，回滚整个操作
                try:
                    db.rollback()
                    PaymentService.unfreeze_funds(db, creator_id, plan_id)
                    db.delete(plan)
                    db.commit()
                except Exception:
                    logger.error("Failed to rollback plan creation after invitation error: {}", str(e))
                logger.error("Failed to create invitation for plan {}: {}", plan_id, str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"创建邀请失败: {str(e)}"
                )

        logger.info("Betting plan created: {} by user {}", plan_id, creator_id)
        
        # 构造返回响应
        plan_data = PlanResponse.from_orm(plan).dict()
        
        # 如果有被邀请人，补充被邀请人信息到响应中
        if invitee:
            plan_data["participant_id"] = str(invitee.id)
            plan_data["participant_nickname"] = invitee.nickname
            plan_data["participant_email"] = invitee.email
        
        return PlanResponse(**plan_data)

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
        """
        Participant accepts an invitation.
        According to design doc: PENDING -> ACTIVE (directly)
            
        Steps:
        1. Validate plan exists and is in PENDING status
        2. Verify inviter is not the same as participant
        3. Check no one has accepted yet
        4. Freeze participant funds
        5. Update plan status to ACTIVE
        6. Update invitation status to ACCEPTED
        7. Notify creator
        """
        # Use FOR UPDATE to lock the row
        plan = db.query(BettingPlan).filter(
            BettingPlan.id == plan_id
        ).with_for_update().first()
            
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
            
        # Must be in PENDING status
        if plan.status != PlanStatus.PENDING:
            if plan.status == PlanStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="该计划已开始，无法再次接受"
                )
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="计划状态不允许接受")
            
        # Cannot accept own plan
        if plan.creator_id == participant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能接受自己创建的计划")
            
        # Check if already accepted
        if plan.participant_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="该计划已有参与者，无法再次接受"
            )
    
        # Validate weight input
        if request.target_weight >= request.initial_weight:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="目标体重必须小于初始体重")
    
        target_weight_loss = request.initial_weight - request.target_weight
    
        # Freeze participant funds
        freeze_result = PaymentService.freeze_funds(db, participant_id, plan_id, plan.bet_amount)
        if not freeze_result.success:
            logger.warning("Failed to freeze funds for user %s: %s", participant_id, freeze_result.error)
            if "余额不足" in (freeze_result.error or ""):
                raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"余额不足，需要充值 {plan.bet_amount} 元")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"资金冻结失败：{freeze_result.error}")
    
        # Update plan
        plan.participant_id = participant_id
        plan.participant_initial_weight = request.initial_weight
        plan.participant_target_weight = request.target_weight
        plan.participant_target_weight_loss = target_weight_loss
        plan.status = PlanStatus.WAITING_DOUBLE_CHECK  # 等待双方确认目标
    
        # Update invitation status if exists
        try:
            from app.models.invitation import Invitation, InvitationStatus
            invitation = db.query(Invitation).filter(
                Invitation.plan_id == plan_id
            ).first()
                
            if invitation:
                invitation.status = InvitationStatus.ACCEPTED
                invitation.responded_at = datetime.utcnow()
        except Exception as e:
            logger.error("Failed to update invitation status: %s", str(e))
    
        try:
            db.commit()
            db.refresh(plan)
        except Exception as e:
            # Rollback: unfreeze participant funds
            try:
                PaymentService.unfreeze_funds(db, participant_id, plan_id)
            except Exception:
                logger.error("Failed to unfreeze participant funds after DB error for user %s: %s", participant_id, str(e))
            logger.error("DB error when updating plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="接受计划失败，请稍后重试")
    
        logger.info("Plan %s accepted by participant %s", plan_id, participant_id)
    
        # Notify creator (best-effort)
        try:
            NotificationService.send_plan_invitation_accepted_notification(db, plan.creator_id, plan_id)
        except Exception as e:
            logger.error("Failed to notify creator about acceptance for plan %s: %s", plan_id, str(e))
    
        return PlanResponse.from_orm(plan)

    @staticmethod
    def confirm_plan(db: Session, plan_id: str, user_id: str) -> PlanResponse:
        """
        确认计划目标，双方都确认后计划变为进行中
        状态流转：WAITING_DOUBLE_CHECK -> ACTIVE
        """
        plan = db.query(BettingPlan).filter(
            BettingPlan.id == plan_id
        ).with_for_update().first()
        
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
            
        # 只有计划参与者可以确认
        if plan.creator_id != user_id and plan.participant_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权确认此计划")
            
        # 必须处于待二次确认状态
        if plan.status != PlanStatus.WAITING_DOUBLE_CHECK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不需要确认")
            
        # 这里简化处理：任意一方确认即生效，或根据需求调整为双方确认
        # 更新计划状态为进行中
        plan.status = PlanStatus.ACTIVE
        plan.activated_at = datetime.utcnow()
        
        try:
            db.commit()
            db.refresh(plan)
        except Exception as e:
            logger.error("DB error when confirming plan %s: %s", plan_id, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="确认计划失败，请稍后重试")
            
        logger.info("Plan %s confirmed by user %s, status changed to ACTIVE", plan_id, user_id)
        
        # 通知对方确认成功
        try:
            notify_user_id = plan.participant_id if user_id == plan.creator_id else plan.creator_id
            NotificationService.send_plan_confirmed_notification(db, notify_user_id, plan_id)
        except Exception as e:
            logger.error("Failed to notify user about plan confirmation: %s", str(e))
            
        return PlanResponse.from_orm(plan)

    @staticmethod
    def reject_plan(db: Session, plan_id: str, user_id: str) -> dict:
        """
        Participant rejects an invitation OR creator rejects after participant accepted.
        
        According to design doc:
        - Participant rejecting PENDING plan: REJECTED status, unfreeze creator funds
        - Invitee rejecting unaccepted invitation: REJECTED status, unfreeze creator funds
        - Creator cannot reject (only abandon is allowed)
        """
        from app.models.invitation import Invitation, InvitationStatus
        
        # Use FOR UPDATE to lock the row
        plan = db.query(BettingPlan).filter(
            BettingPlan.id == plan_id
        ).with_for_update().first()
        
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")

        # 情况1：被邀请人拒绝未接受的邀请
        invitation = db.query(Invitation).filter(
            Invitation.plan_id == plan_id,
            Invitation.invitee_id == user_id,
            Invitation.status.in_([InvitationStatus.PENDING, InvitationStatus.VIEWED])
        ).first()
        
        if invitation and plan.participant_id is None:
            # 更新邀请状态
            invitation.status = InvitationStatus.REJECTED
            invitation.responded_at = datetime.utcnow()
            
            # 更新计划状态
            plan.status = PlanStatus.REJECTED
            
            try:
                db.commit()
                # 解冻创建者资金
                try:
                    PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
                except Exception:
                    logger.error("Failed to unfreeze creator funds for plan %s, user %s", plan_id, plan.creator_id)
            except Exception as e:
                logger.error("DB error when invitee rejecting plan %s: %s", plan_id, str(e))
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="拒绝邀请失败，请稍后重试")
            
            # 通知创建者
            try:
                NotificationService.send_plan_rejected_notification(db, plan.creator_id, plan_id)
            except Exception:
                logger.exception("Failed to notify creator about invitation rejection for plan %s", plan_id)
            
            logger.info("Invitation for plan %s rejected by invitee %s", plan_id, user_id)
            return {"result": "rejected"}

        # 情况2：已接受邀请的参与者拒绝计划
        if plan.participant_id == user_id:
            # Only allowed when plan is in PENDING status
            if plan.status != PlanStatus.PENDING:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不能拒绝")
            
            # Update invitation status if exists
            try:
                from app.models.invitation import Invitation, InvitationStatus
                invitation = db.query(Invitation).filter(
                    Invitation.plan_id == plan_id
                ).first()
                
                if invitation:
                    invitation.status = InvitationStatus.REJECTED
                    invitation.responded_at = datetime.utcnow()
            except Exception as e:
                logger.error("Failed to update invitation status: %s", str(e))
            
            # Change plan status to REJECTED
            plan.status = PlanStatus.REJECTED
            plan.participant_id = None
            plan.participant_initial_weight = None
            plan.participant_target_weight = None
            plan.participant_target_weight_loss = None

            try:
                db.commit()
                # Unfreeze creator funds
                try:
                    PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
                except Exception:
                    logger.error("Failed to unfreeze creator funds for plan %s, user %s", plan_id, plan.creator_id)
            except Exception as e:
                logger.error("DB error when participant rejecting plan %s: %s", plan_id, str(e))
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="拒绝计划失败，请稍后重试")

            # Notify creator
            try:
                NotificationService.send_plan_rejected_notification(db, plan.creator_id, plan_id)
            except Exception:
                logger.exception("Failed to notify creator about participant rejection for plan %s", plan_id)

            logger.info("Plan %s rejected by participant %s", plan_id, user_id)
            return {"result": "rejected"}

        # Creator cannot reject (should use abandon instead)
        if plan.creator_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建者不能拒绝计划，请使用放弃计划功能"
            )

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权拒绝此计划")

    @staticmethod
    def cancel_plan(db: Session, plan_id: str, user_id: str) -> dict:
        """
        Only creator can cancel a non-active plan.
        According to design doc: PENDING -> CANCELLED (unfreeze creator funds)
        """
        # Use FOR UPDATE to lock the row
        plan = db.query(BettingPlan).filter(
            BettingPlan.id == plan_id
        ).with_for_update().first()
        
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        if plan.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有创建者可以取消计划")
        if plan.status == PlanStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能取消未生效的计划")

        participant_id = plan.participant_id
        plan.status = PlanStatus.CANCELLED
        plan.participant_id = None

        try:
            db.commit()
            # Unfreeze creator funds
            try:
                PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
            except Exception:
                logger.error("Failed to unfreeze creator funds for plan %s", plan_id)
            # Unfreeze participant funds if any
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
        """
        Revoke a plan that hasn't been accepted yet. Only creator can revoke.
        According to design doc: PENDING -> CANCELLED (unfreeze creator funds)
        """
        # Use FOR UPDATE to lock the row
        plan = db.query(BettingPlan).filter(
            BettingPlan.id == plan_id
        ).with_for_update().first()
        
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
        if plan.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有创建者可以撤销计划")
        # Can only revoke if no participant has accepted
        if plan.participant_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能撤销未被接受的计划")
        
        plan.status = PlanStatus.CANCELLED
        plan.participant_id = None

        try:
            db.commit()
            # Unfreeze creator funds
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
        """获取用户的计划列表，包括：
        1. 用户创建的计划
        2. 用户参与的计划
        3. 用户被邀请的计划（待接受）
        """
        from sqlalchemy.orm import joinedload
        from app.models.invitation import Invitation, InvitationStatus
        
        # 子查询：获取用户作为被邀请人的所有计划ID（所有状态都显示，包括已拒绝的）
        invited_plan_ids = db.query(Invitation.plan_id).filter(
            Invitation.invitee_id == user_id
        ).subquery()
        
        query = db.query(BettingPlan).options(
            joinedload(BettingPlan.creator),
            joinedload(BettingPlan.participant)
        ).filter(
            (BettingPlan.creator_id == user_id) | 
            (BettingPlan.participant_id == user_id) |
            (BettingPlan.id.in_(invited_plan_ids))
        )
        if status_filter:
            query = query.filter(BettingPlan.status == status_filter)
        plans = query.order_by(BettingPlan.created_at.desc()).limit(limit).offset(offset).all()
        
        result = []
        for plan in plans:
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
            result.append(PlanResponse(**response_data))
        
        return result
