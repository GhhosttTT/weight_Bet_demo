import uuid
from datetime import datetime, timedelta

from app.services.invitation_service import InvitationService
from app.services.betting_plan_service import BettingPlanService
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.invitation import InvitationStatus


def test_pending_actions_invitations_and_doublecheck(db_session, test_users, test_plan):
    creator = test_users["creator"]
    invitee = test_users["invitee"]
    other = test_users["other"]
    plan = test_plan

    # 创建邀请
    invitation = InvitationService.create_invitation(
        db=db_session,
        plan_id=plan.id,
        inviter_id=creator.id,
        invitee_email=invitee.email
    )

    # 被邀请者尚未查看，调用 pending actions 应该包含该邀请
    from app.api.pending_actions import get_pending_actions

    pending_for_invitee = get_pending_actions(current_user_id=invitee.id, db=db_session)
    assert any(inv["id"] == invitation.id for inv in pending_for_invitee["invitations"])

    # 创建另一个计划并让其他用户接受，触发 creator double-check
    plan2 = BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=creator.id,
        status=PlanStatus.PENDING,
        bet_amount=50.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=10),
        creator_initial_weight=80.0,
        creator_target_weight=75.0,
        creator_target_weight_loss=5.0
    )
    db_session.add(plan2)
    db_session.commit()

    # other 接受 plan2
    from app.schemas.betting_plan import AcceptPlanRequest
    req = AcceptPlanRequest(initial_weight=85.0, target_weight=78.0)
    BettingPlanService.accept_plan(db=db_session, plan_id=plan2.id, participant_id=other.id, request=req)

    # pending actions for creator should include doubleChecks for plan2
    pending_for_creator = get_pending_actions(current_user_id=creator.id, db=db_session)
    assert any(dc["planId"] == plan2.id for dc in pending_for_creator["doubleChecks"])

