import uuid
from datetime import datetime, timedelta
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.invitation_service import InvitationService
from app.services.betting_plan_service import BettingPlanService
from app.services.payment_service import PaymentService
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.invitation import InvitationStatus
from app.models.user import User, Gender
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionStatus, TransactionType


@pytest.fixture
def db_session():
    """创建独立测试数据库会话。"""
    from app.database import SessionLocal, engine, Base

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_users(db_session: Session):
    """创建带有资金账户的待处理动作测试用户。"""
    users = {
        "creator": User(
            id=str(uuid.uuid4()), email="pending_creator@example.com",
            password_hash="hashed_password", nickname="创建者",
            gender=Gender.MALE, age=30, height=175.0, current_weight=80.0
        ),
        "invitee": User(
            id=str(uuid.uuid4()), email="pending_invitee@example.com",
            password_hash="hashed_password", nickname="被邀请者",
            gender=Gender.FEMALE, age=25, height=165.0, current_weight=60.0
        ),
        "other": User(
            id=str(uuid.uuid4()), email="pending_other@example.com",
            password_hash="hashed_password", nickname="其他用户",
            gender=Gender.OTHER, age=28, height=170.0, current_weight=70.0
        ),
    }
    for user in users.values():
        db_session.add(user)
        db_session.add(Balance(
            user_id=user.id, available_balance=1000.0, frozen_balance=0.0
        ))
    db_session.commit()
    return users


@pytest.fixture
def test_plan(db_session: Session, test_users):
    """创建待邀请的计划。"""
    plan = BettingPlan(
        id=str(uuid.uuid4()), creator_id=test_users["creator"].id,
        status=PlanStatus.PENDING, bet_amount=100.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        creator_initial_weight=80.0, creator_target_weight=75.0,
        creator_target_weight_loss=5.0
    )
    db_session.add(plan)
    db_session.commit()
    return plan


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


def test_specified_invitation_cannot_be_accepted_by_other_user(
    db_session, test_users, test_plan
):
    """指定邀请不能被其他用户抢先接受。"""
    creator = test_users["creator"]
    invitee = test_users["invitee"]
    other = test_users["other"]

    InvitationService.create_invitation(
        db=db_session,
        plan_id=test_plan.id,
        inviter_id=creator.id,
        invitee_email=invitee.email,
    )

    from app.schemas.betting_plan import AcceptPlanRequest
    request = AcceptPlanRequest(initial_weight=85.0, target_weight=78.0)
    with pytest.raises(HTTPException) as exc_info:
        BettingPlanService.accept_plan(
            db=db_session,
            plan_id=test_plan.id,
            participant_id=other.id,
            request=request,
        )

    assert exc_info.value.status_code == 403
    assert "被邀请用户" in exc_info.value.detail


def test_participant_can_reject_after_accepting_and_gets_refund(
    db_session, test_users, test_plan
):
    """待二次确认阶段拒绝时，双方冻结资金都应解冻。"""
    creator = test_users["creator"]
    invitee = test_users["invitee"]

    # 为手工构造的测试计划补齐创建者冻结流水。
    creator_balance = db_session.query(Balance).filter(
        Balance.user_id == creator.id
    ).one()
    creator_balance.available_balance = 900.0
    creator_balance.frozen_balance = 100.0
    db_session.add(Transaction(
        id=str(uuid.uuid4()),
        user_id=creator.id,
        type=TransactionType.FREEZE,
        amount=100.0,
        status=TransactionStatus.COMPLETED,
        related_plan_id=test_plan.id,
        completed_at=datetime.utcnow(),
    ))
    db_session.commit()

    InvitationService.create_invitation(
        db=db_session,
        plan_id=test_plan.id,
        inviter_id=creator.id,
        invitee_email=invitee.email,
    )
    from app.schemas.betting_plan import AcceptPlanRequest
    BettingPlanService.accept_plan(
        db=db_session,
        plan_id=test_plan.id,
        participant_id=invitee.id,
        request=AcceptPlanRequest(initial_weight=85.0, target_weight=78.0),
    )

    result = BettingPlanService.reject_plan(db_session, test_plan.id, invitee.id)

    assert result["result"] == "rejected"
    creator_balance = db_session.query(Balance).filter(
        Balance.user_id == creator.id
    ).one()
    invitee_balance = db_session.query(Balance).filter(
        Balance.user_id == invitee.id
    ).one()
    assert creator_balance.available_balance == 1000.0
    assert creator_balance.frozen_balance == 0.0
    assert invitee_balance.available_balance == 1000.0
    assert invitee_balance.frozen_balance == 0.0


def test_terminal_plan_cannot_be_cancelled_or_revoked(
    db_session, test_users, test_plan
):
    """终态计划不能再次进入取消或撤销流程。"""
    creator = test_users["creator"]

    test_plan.status = PlanStatus.COMPLETED
    db_session.commit()
    with pytest.raises(HTTPException) as cancel_error:
        BettingPlanService.cancel_plan(db_session, test_plan.id, creator.id)
    assert cancel_error.value.status_code == 400

    test_plan.status = PlanStatus.EXPIRED
    db_session.commit()
    with pytest.raises(HTTPException) as revoke_error:
        BettingPlanService.revoke_plan(db_session, test_plan.id, creator.id)
    assert revoke_error.value.status_code == 400


def test_cancel_rolls_back_status_when_refund_fails(
    db_session, test_users, test_plan, monkeypatch
):
    """资金解冻失败时，取消状态也必须回滚。"""
    creator = test_users["creator"]
    monkeypatch.setattr(PaymentService, "unfreeze_funds", lambda *args, **kwargs: False)

    with pytest.raises(HTTPException) as exc_info:
        BettingPlanService.cancel_plan(db_session, test_plan.id, creator.id)

    assert exc_info.value.status_code == 500
    db_session.refresh(test_plan)
    assert test_plan.status == PlanStatus.PENDING

