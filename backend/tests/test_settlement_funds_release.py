import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.balance import Balance
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import Gender, User
from app.services.payment_service import PaymentService


def _user(db, user_id):
    db.add(User(
        id=user_id,
        email=f"{user_id}@example.com",
        password_hash="hash",
        nickname=user_id,
        gender=Gender.OTHER,
        age=30,
        height=170,
        current_weight=80,
        target_weight=70,
        created_at=datetime.utcnow(),
    ))
    db.add(Balance(user_id=user_id, available_balance=0, frozen_balance=100))


def test_settlement_release_is_atomic_and_idempotent():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    creator_id = str(uuid.uuid4())
    participant_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    settlement_id = str(uuid.uuid4())

    try:
        _user(db, creator_id)
        _user(db, participant_id)
        db.add(BettingPlan(
            id=plan_id,
            creator_id=creator_id,
            participant_id=participant_id,
            status=PlanStatus.ACTIVE,
            bet_amount=100,
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
            creator_initial_weight=80,
            creator_target_weight=70,
            creator_target_weight_loss=10,
            participant_initial_weight=80,
            participant_target_weight=70,
            participant_target_weight_loss=10,
            created_at=datetime.utcnow(),
        ))
        for user_id in (creator_id, participant_id):
            db.add(Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                type=TransactionType.FREEZE,
                amount=100,
                status=TransactionStatus.COMPLETED,
                related_plan_id=plan_id,
                completed_at=datetime.utcnow(),
            ))
        db.commit()

        assert PaymentService.release_settlement_funds(
            db, creator_id, plan_id, 170, settlement_id
        )
        assert PaymentService.release_settlement_funds(
            db, participant_id, plan_id, 0, settlement_id
        )
        db.commit()

        creator = db.query(Balance).filter(Balance.user_id == creator_id).one()
        participant = db.query(Balance).filter(Balance.user_id == participant_id).one()
        assert (creator.available_balance, creator.frozen_balance) == (170, 0)
        assert (participant.available_balance, participant.frozen_balance) == (0, 0)

        # 同一冻结流水不能再次释放，避免重放请求增加余额。
        assert not PaymentService.release_settlement_funds(
            db, creator_id, plan_id, 170, str(uuid.uuid4())
        )
        db.rollback()
        creator = db.query(Balance).filter(Balance.user_id == creator_id).one()
        assert (creator.available_balance, creator.frozen_balance) == (170, 0)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_freeze_and_unfreeze_are_idempotent():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    user_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())

    try:
        db.add(User(
            id=user_id,
            email=f"{user_id}@example.com",
            password_hash="hash",
            nickname="retry-user",
            gender=Gender.OTHER,
            age=30,
            height=170,
            current_weight=80,
            target_weight=70,
            created_at=datetime.utcnow(),
        ))
        db.add(Balance(user_id=user_id, available_balance=100, frozen_balance=0))
        db.commit()

        first = PaymentService.freeze_funds(db, user_id, plan_id, 25)
        second = PaymentService.freeze_funds(db, user_id, plan_id, 25)
        assert first.success and second.success
        assert first.transaction_id == second.transaction_id

        assert PaymentService.unfreeze_funds(db, user_id, plan_id)
        assert PaymentService.unfreeze_funds(db, user_id, plan_id)

        balance = db.query(Balance).filter(Balance.user_id == user_id).one()
        assert balance.available_balance == 100
        assert balance.frozen_balance == 0
        assert db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.related_plan_id == plan_id,
            Transaction.type == TransactionType.UNFREEZE,
        ).count() == 1
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_charge_and_withdraw_use_locked_balance_and_minimum_amount():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    user_id = str(uuid.uuid4())

    try:
        db.add(User(
            id=user_id,
            email=f"{user_id}@example.com",
            password_hash="hash",
            nickname="cash-user",
            gender=Gender.OTHER,
            age=30,
            height=170,
            current_weight=80,
            target_weight=70,
            created_at=datetime.utcnow(),
        ))
        db.add(Balance(user_id=user_id, available_balance=10, frozen_balance=0))
        db.commit()

        with pytest.raises(Exception) as exc_info:
            PaymentService.charge_funds(db, user_id, 0.001)
        assert exc_info.value.detail == "金额必须至少为 0.01"

        result = PaymentService.withdraw_funds(db, user_id, 0.001)
        assert result.success is False
        assert result.error == "金额必须至少为 0.01"

        balance = db.query(Balance).filter(Balance.user_id == user_id).one()
        assert balance.available_balance == 10
        assert db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.CHARGE,
        ).count() == 0
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_charge_uses_half_up_cent_rounding():
    """金额规范化应遵循财务常用的半入规则。"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    user_id = str(uuid.uuid4())

    try:
        db.add(User(
            id=user_id,
            email=f"{user_id}@example.com",
            password_hash="hash",
            nickname="rounding-user",
            gender=Gender.OTHER,
            age=30,
            height=170,
            current_weight=80,
            target_weight=70,
            created_at=datetime.utcnow(),
        ))
        db.add(Balance(user_id=user_id, available_balance=10, frozen_balance=0))
        db.commit()

        balance = PaymentService.charge_funds(db, user_id, 100.005)

        assert balance.available_balance == 110.01
        transaction = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.CHARGE,
        ).one()
        assert transaction.amount == 100.01
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
