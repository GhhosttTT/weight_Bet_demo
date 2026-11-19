"""拒绝计划时，计划状态与资金解冻必须原子完成。"""

from datetime import datetime, timedelta
import uuid

import pytest
from fastapi import HTTPException

from app.database import Base, SessionLocal, engine
from app.models.balance import Balance
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.invitation import Invitation, InvitationStatus
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import Gender, User
from app.services.betting_plan_service import BettingPlanService
from app.services.payment_service import PaymentService


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)


def _user(email: str) -> User:
    return User(
        id=str(uuid.uuid4()),
        email=email,
        password_hash="hashed-password",
        nickname=email.split("@")[0],
        gender=Gender.MALE,
        age=30,
        height=175,
        current_weight=80,
        target_weight=70,
    )


def _plan(creator: User, participant: User) -> BettingPlan:
    now = datetime.utcnow()
    return BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=creator.id,
        participant_id=participant.id,
        status=PlanStatus.WAITING_DOUBLE_CHECK,
        bet_amount=100,
        start_date=now,
        end_date=now + timedelta(days=7),
        creator_initial_weight=80,
        creator_target_weight=70,
        creator_target_weight_loss=10,
        participant_initial_weight=90,
        participant_target_weight=80,
        participant_target_weight_loss=10,
    )


def _invitation(plan: BettingPlan, creator: User, participant: User) -> Invitation:
    return Invitation(
        id=str(uuid.uuid4()),
        plan_id=plan.id,
        inviter_id=creator.id,
        invitee_id=participant.id,
        invitee_email=participant.email,
        status=InvitationStatus.ACCEPTED,
    )


def test_participant_rejection_rolls_back_plan_when_refund_is_incomplete(db_session, monkeypatch):
    creator = _user("creator-atomic@example.com")
    participant = _user("participant-atomic@example.com")
    plan = _plan(creator, participant)
    db_session.add_all([
        creator,
        participant,
        plan,
        _invitation(plan, creator, participant),
        Balance(user_id=creator.id, available_balance=900, frozen_balance=100),
        Balance(user_id=participant.id, available_balance=1000, frozen_balance=0),
        Transaction(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            type=TransactionType.FREEZE,
            amount=100,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan.id,
        ),
    ])
    db_session.commit()

    monkeypatch.setattr(
        "app.services.betting_plan_service.NotificationService.send_plan_rejected_notification",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(HTTPException) as error:
        BettingPlanService.reject_plan(db_session, plan.id, participant.id)
    assert error.value.status_code == 500

    db_session.expire_all()
    persisted_plan = db_session.query(BettingPlan).filter_by(id=plan.id).one()
    creator_balance = db_session.query(Balance).filter_by(user_id=creator.id).one()
    assert persisted_plan.status == PlanStatus.WAITING_DOUBLE_CHECK
    assert persisted_plan.participant_id == participant.id
    assert creator_balance.available_balance == 900
    assert creator_balance.frozen_balance == 100
    assert db_session.query(Transaction).filter(
        Transaction.related_plan_id == plan.id,
        Transaction.type == TransactionType.UNFREEZE,
    ).count() == 0


def test_participant_rejection_refunds_both_users_atomically(db_session, monkeypatch):
    creator = _user("creator-success@example.com")
    participant = _user("participant-success@example.com")
    plan = _plan(creator, participant)
    db_session.add_all([
        creator,
        participant,
        plan,
        _invitation(plan, creator, participant),
        Balance(user_id=creator.id, available_balance=900, frozen_balance=100),
        Balance(user_id=participant.id, available_balance=900, frozen_balance=100),
        Transaction(
            id=str(uuid.uuid4()), user_id=creator.id, type=TransactionType.FREEZE,
            amount=100, status=TransactionStatus.COMPLETED, related_plan_id=plan.id,
        ),
        Transaction(
            id=str(uuid.uuid4()), user_id=participant.id, type=TransactionType.FREEZE,
            amount=100, status=TransactionStatus.COMPLETED, related_plan_id=plan.id,
        ),
    ])
    db_session.commit()

    monkeypatch.setattr(
        "app.services.betting_plan_service.NotificationService.send_plan_rejected_notification",
        lambda *args, **kwargs: None,
    )

    result = BettingPlanService.reject_plan(db_session, plan.id, participant.id)
    assert result == {"result": "rejected"}

    db_session.expire_all()
    persisted_plan = db_session.query(BettingPlan).filter_by(id=plan.id).one()
    assert persisted_plan.status == PlanStatus.REJECTED
    for user in (creator, participant):
        balance = db_session.query(Balance).filter_by(user_id=user.id).one()
        assert balance.available_balance == 1000
        assert balance.frozen_balance == 0
        assert db_session.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.related_plan_id == plan.id,
            Transaction.type == TransactionType.UNFREEZE,
            Transaction.status == TransactionStatus.COMPLETED,
        ).count() == 1


def test_freeze_is_idempotent_for_same_user_and_plan(db_session):
    creator = _user("creator-freeze@example.com")
    plan = _plan(creator, creator)
    plan.participant_id = None
    db_session.add_all([
        creator,
        plan,
        Balance(user_id=creator.id, available_balance=200, frozen_balance=0),
    ])
    db_session.commit()

    first = PaymentService.freeze_funds(db_session, creator.id, plan.id, 100)
    second = PaymentService.freeze_funds(db_session, creator.id, plan.id, 100)

    assert first.success is True
    assert second.success is True
    assert second.transaction_id == first.transaction_id
    assert db_session.query(Transaction).filter(
        Transaction.user_id == creator.id,
        Transaction.related_plan_id == plan.id,
        Transaction.type == TransactionType.FREEZE,
    ).count() == 1
    balance = db_session.query(Balance).filter_by(user_id=creator.id).one()
    assert balance.available_balance == 100
    assert balance.frozen_balance == 100
