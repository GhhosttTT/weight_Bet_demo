from typing import List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.invitation import Invitation, InvitationStatus
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.settlement import Settlement
from app.models.settlement_choice import SettlementChoice

router = APIRouter()


@router.get("/me/pending-actions")
def get_pending_actions(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    返回当前用户的一次性待处理项：
    - invitations: 被邀请者尚未查看的邀请（status == pending）
    - doubleChecks: 需要创建者确认的计划（creator 为当前用户, status == waiting_double_check, 有 participant）
    - settlements: 需要用户进行结算的计划（计划已到期，用户是参与者之一，尚未结算）
    """
    now = datetime.utcnow()

    # invitations for which current user is the invitee and still pending
    invitations = db.query(Invitation).filter(
        Invitation.invitee_id == current_user_id,
        Invitation.status == InvitationStatus.PENDING
    ).order_by(Invitation.sent_at.desc()).all()

    invitations_payload = [
        {
            "id": inv.id,
            "planId": inv.plan_id,
            "fromUserId": inv.inviter_id,
            "message": inv.plan.description if inv.plan else None,
            "type": "invite",
            "isFirstTime": True
        }
        for inv in invitations
    ]

    # double checks: plans where current user is creator, status is waiting_double_check and a participant exists
    double_checks = db.query(BettingPlan).filter(
        BettingPlan.creator_id == current_user_id,
        BettingPlan.status == PlanStatus.WAITING_DOUBLE_CHECK,
        BettingPlan.participant_id != None
    ).order_by(BettingPlan.created_at.desc()).all()

    double_checks_payload = [
        {
            "planId": p.id,
            "initiatorId": p.participant_id,
            "reason": "participant_submitted_goal",
            "isPending": True
        }
        for p in double_checks
    ]

    # settlements: plans that have ended and need settlement
    # Check for plans where:
    # 1. Current user is a participant (creator or participant)
    # 2. Plan is ACTIVE
    # 3. Plan end date is in the past
    # 4. No settlement exists yet
    plans_for_settlement = db.query(BettingPlan).filter(
        and_(
            (BettingPlan.creator_id == current_user_id) | (BettingPlan.participant_id == current_user_id),
            BettingPlan.status == PlanStatus.ACTIVE,
            BettingPlan.end_date <= now
        )
    ).order_by(BettingPlan.end_date.desc()).all()

    # Filter out plans that already have a settlement
    settlement_payload = []
    for plan in plans_for_settlement:
        existing_settlement = db.query(Settlement).filter(Settlement.plan_id == plan.id).first()
        if not existing_settlement:
            settlement_payload.append({
                "planId": plan.id,
                "isPending": True
            })

    return {
        "invitations": invitations_payload,
        "doubleChecks": double_checks_payload,
        "settlements": settlement_payload
    }

