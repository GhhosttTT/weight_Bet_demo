"""
邀请服务
"""
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.invitation import Invitation, InvitationStatus
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.user import User
from app.services.friend_search_service import FriendSearchService
from app.services.notification_service import NotificationService
from app.logger import get_logger

logger = get_logger()


class InvitationService:
    """邀请服务类"""
    
    @staticmethod
    def create_invitation(
        db: Session,
        plan_id: str,
        inviter_id: str,
        invitee_email: str
    ) -> Invitation:
        """
        创建邀请记录
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            inviter_id: 邀请者 ID
            invitee_email: 被邀请者邮箱
            
        Returns:
            Invitation: 创建的邀请对象
            
        Raises:
            HTTPException: 各种验证失败的情况
        """
        # 步骤 1: 验证计划
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            logger.warning("Plan not found: {}", plan_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )
        
        # 验证邀请者是计划创建者
        if plan.creator_id != inviter_id:
            logger.warning(
                "User {} is not the creator of plan {}",
                inviter_id, plan_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有创建者可以邀请好友"
            )
        
        # 验证计划状态
        if plan.status != PlanStatus.PENDING:
            logger.warning(
                "Plan {} is not in PENDING status: {}",
                plan_id, plan.status
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划状态不允许邀请"
            )
        
        # 步骤 2: 验证邮箱格式
        if not FriendSearchService.validate_email_format(invitee_email):
            logger.warning("Invalid email format: {}", invitee_email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式无效"
            )
        
        # 步骤 3: 检查是否已存在邀请
        # 只视为重复邀请当且仅当同一计划已对相同邮箱发出邀请
        # 使用不区分大小写的比较以避免大小写产生的重复问题
        try:
            from sqlalchemy import func
            existing_invitation = db.query(Invitation).filter(
                Invitation.plan_id == plan_id,
                func.lower(Invitation.invitee_email) == invitee_email.lower()
            ).first()
        except Exception:
            # 如果 sqlalchemy.func 不可用则回退到简单比较
            existing_invitation = db.query(Invitation).filter(
                Invitation.plan_id == plan_id,
                Invitation.invitee_email == invitee_email
            ).first()
        if existing_invitation:
            logger.warning("Invitation already exists for plan {} and email {}", plan_id, invitee_email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该用户已被邀请"
            )
        
        # 步骤 4: 搜索被邀请用户
        invitee = db.query(User).filter(User.email == invitee_email).first()
        
        if not invitee:
            logger.warning("User not found for email: {}", invitee_email)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证不能邀请自己
        if invitee.id == inviter_id:
            logger.warning("User {} tried to invite themselves", inviter_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能邀请自己"
            )
        
        # 步骤 5: 创建邀请记录
        invitation = Invitation(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            inviter_id=inviter_id,
            invitee_email=invitee_email,
            invitee_id=invitee.id,
            status=InvitationStatus.PENDING,
            sent_at=datetime.utcnow()
        )
        
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        logger.info(
            "Invitation created: id={}, plan_id={}, inviter_id={}, invitee_id={}",
            invitation.id, plan_id, inviter_id, invitee.id
        )
        
        # 步骤 6: 发送通知
        try:
            # 计算计划时长（天数）
            duration_days = (plan.end_date - plan.start_date).days
            
            # 构建通知数据
            notification_data = {
                "invitation_id": invitation.id,
                "plan_id": plan_id,
                "inviter_name": plan.creator.nickname,
                "bet_amount": plan.bet_amount,
                "target_weight_loss": plan.creator_target_weight_loss,
                "duration_days": duration_days
            }
            
            # 发送邀请通知
            NotificationService.send_plan_invitation_notification(
                db=db,
                user_id=invitee.id,
                plan_id=plan_id,
                creator_name=plan.creator.nickname
            )
            
            logger.info(
                "Invitation notification sent to user {}",
                invitee.id
            )
        except Exception as e:
            # 通知发送失败不应影响邀请创建
            logger.error(
                "Failed to send invitation notification: {}",
                str(e)
            )
        
        return invitation
    
    @staticmethod
    def get_invitation_by_plan(
        db: Session,
        plan_id: str
    ) -> Optional[Invitation]:
        """
        根据计划 ID 获取邀请
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            
        Returns:
            Optional[Invitation]: 邀请对象，如果不存在则返回 None
        """
        invitation = db.query(Invitation).filter(
            Invitation.plan_id == plan_id
        ).first()
        
        return invitation
    
    @staticmethod
    def get_user_invitations(
        db: Session,
        user_id: str,
        status: Optional[InvitationStatus] = None
    ) -> List[Invitation]:
        """
        获取用户的邀请列表
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            status: 可选的状态筛选
            
        Returns:
            List[Invitation]: 邀请列表
        """
        query = db.query(Invitation).filter(
            Invitation.invitee_id == user_id
        )
        
        if status:
            query = query.filter(Invitation.status == status)
        
        invitations = query.order_by(Invitation.sent_at.desc()).all()
        
        return invitations
    
    @staticmethod
    def update_invitation_status(
        db: Session,
        invitation_id: str,
        new_status: InvitationStatus,
        response_time: datetime
    ) -> Invitation:
        """
        更新邀请状态
        
        Args:
            db: 数据库会话
            invitation_id: 邀请 ID
            new_status: 新状态
            response_time: 响应时间
            
        Returns:
            Invitation: 更新后的邀请对象
            
        Raises:
            HTTPException: 邀请不存在
        """
        invitation = db.query(Invitation).filter(
            Invitation.id == invitation_id
        ).first()
        
        if not invitation:
            logger.warning("Invitation not found: {}", invitation_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="邀请不存在"
            )
        
        # 更新状态
        invitation.status = new_status
        
        # 根据状态更新相应的时间戳
        if new_status == InvitationStatus.VIEWED:
            invitation.viewed_at = response_time
        elif new_status in [InvitationStatus.ACCEPTED, InvitationStatus.REJECTED]:
            invitation.responded_at = response_time
        
        db.commit()
        db.refresh(invitation)
        
        logger.info(
            "Invitation status updated: id={}, status={}",
            invitation_id, new_status
        )
        
        return invitation
