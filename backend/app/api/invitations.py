"""
邀请 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.services.invitation_service import InvitationService
from app.models.invitation import InvitationStatus

router = APIRouter()


class InviteFriendRequest(BaseModel):
    """邀请好友请求"""
    invitee_email: EmailStr


class InvitationResponse(BaseModel):
    """邀请响应"""
    invitation_id: str
    plan_id: str
    inviter_id: str
    invitee_email: str
    invitee_id: Optional[str]
    status: str
    sent_at: str
    viewed_at: Optional[str]
    responded_at: Optional[str]


@router.post("/betting-plans/{plan_id}/invite")
def invite_friend_to_plan(
    plan_id: str,
    request: InviteFriendRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    邀请好友参与减肥计划
    
    - **plan_id**: 计划 ID
    - **invitee_email**: 被邀请者邮箱
    
    返回创建的邀请对象
    """
    invitation = InvitationService.create_invitation(
        db=db,
        plan_id=plan_id,
        inviter_id=current_user_id,
        invitee_email=request.invitee_email
    )
    
    return {
        "invitation_id": invitation.id,
        "plan_id": invitation.plan_id,
        "inviter_id": invitation.inviter_id,
        "invitee_email": invitation.invitee_email,
        "invitee_id": invitation.invitee_id,
        "status": invitation.status.value,
        "sent_at": invitation.sent_at.isoformat() if invitation.sent_at else None,
        "viewed_at": invitation.viewed_at.isoformat() if invitation.viewed_at else None,
        "responded_at": invitation.responded_at.isoformat() if invitation.responded_at else None
    }


@router.get("/invitations")
def get_user_invitations(
    status: Optional[str] = Query(None, description="邀请状态筛选"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的邀请列表
    
    - **status**: 可选的状态筛选（pending, viewed, accepted, rejected, expired）
    
    返回邀请列表
    """
    # 验证状态参数
    invitation_status = None
    if status:
        try:
            invitation_status = InvitationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {status}"
            )
    
    invitations = InvitationService.get_user_invitations(
        db=db,
        user_id=current_user_id,
        status=invitation_status
    )
    
    return {
        "invitations": [
            {
                "invitation_id": inv.id,
                "plan_id": inv.plan_id,
                "inviter_id": inv.inviter_id,
                "inviter_name": inv.inviter.nickname if inv.inviter else None,
                "invitee_email": inv.invitee_email,
                "status": inv.status.value,
                "sent_at": inv.sent_at.isoformat() if inv.sent_at else None,
                "viewed_at": inv.viewed_at.isoformat() if inv.viewed_at else None,
                "responded_at": inv.responded_at.isoformat() if inv.responded_at else None,
                # 计划信息
                "bet_amount": inv.plan.bet_amount if inv.plan else None,
                "target_weight_loss": inv.plan.creator_target_weight_loss if inv.plan else None,
                "duration_days": (inv.plan.end_date - inv.plan.start_date).days if inv.plan else None,
                "start_date": inv.plan.start_date.isoformat() if inv.plan and inv.plan.start_date else None,
                "end_date": inv.plan.end_date.isoformat() if inv.plan and inv.plan.end_date else None
            }
            for inv in invitations
        ],
        "total": len(invitations)
    }


@router.get("/invitations/{invitation_id}")
def get_invitation_details(
    invitation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取邀请详情
    
    - **invitation_id**: 邀请 ID
    
    返回邀请详情和完整计划信息
    """
    from app.models.invitation import Invitation
    
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请不存在"
        )
    
    # 验证权限：只有邀请者或被邀请者可以查看
    if invitation.inviter_id != current_user_id and invitation.invitee_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此邀请"
        )
    
    plan = invitation.plan
    
    return {
        "invitation_id": invitation.id,
        "status": invitation.status.value,
        "sent_at": invitation.sent_at.isoformat() if invitation.sent_at else None,
        "viewed_at": invitation.viewed_at.isoformat() if invitation.viewed_at else None,
        "responded_at": invitation.responded_at.isoformat() if invitation.responded_at else None,
        # 完整计划信息
        "plan": {
            "plan_id": plan.id,
            "creator_id": plan.creator_id,
            "creator_name": plan.creator.nickname if plan.creator else None,
            "bet_amount": plan.bet_amount,
            "start_date": plan.start_date.isoformat() if plan.start_date else None,
            "end_date": plan.end_date.isoformat() if plan.end_date else None,
            "creator_initial_weight": plan.creator_initial_weight,
            "creator_target_weight": plan.creator_target_weight,
            "creator_target_weight_loss": plan.creator_target_weight_loss,
            "description": plan.description,
            "status": plan.status.value
        }
    }


@router.post("/invitations/{invitation_id}/view")
def mark_invitation_viewed(
    invitation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    标记邀请为已查看
    
    - **invitation_id**: 邀请 ID
    
    更新 viewed_at 时间戳和状态
    """
    from datetime import datetime
    from app.models.invitation import Invitation
    
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请不存在"
        )
    
    # 验证权限：只有被邀请者可以标记为已查看
    if invitation.invitee_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有被邀请者可以标记为已查看"
        )
    
    # 更新状态
    updated_invitation = InvitationService.update_invitation_status(
        db=db,
        invitation_id=invitation_id,
        new_status=InvitationStatus.VIEWED,
        response_time=datetime.utcnow()
    )
    
    return {
        "invitation_id": updated_invitation.id,
        "status": updated_invitation.status.value,
        "viewed_at": updated_invitation.viewed_at.isoformat() if updated_invitation.viewed_at else None,
        "message": "邀请已标记为已查看"
    }


@router.post("/invitations/{invitation_id}/mark-seen")
def mark_invitation_seen(
    invitation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    标记邀请已展示（兼容客户端命名）
    - 限制：只有被邀请者可以标记
    """
    # 直接调用现有的标记为已查看逻辑
    return mark_invitation_viewed(invitation_id, current_user_id, db)
