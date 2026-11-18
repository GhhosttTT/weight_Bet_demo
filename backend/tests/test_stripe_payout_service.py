"""Stripe Connect 提现流程测试。"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import Gender, User
from app.services.stripe_payout_service import StripePayoutService


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    db.add(User(
        id="payout-user-001", email="payout@example.com", password_hash="hash",
        nickname="Payout User", gender=Gender.OTHER, age=30, height=170, current_weight=70,
    ))
    db.add(Balance(user_id="payout-user-001", available_balance=100, frozen_balance=0))
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def stripe_config(monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_realistic")


def test_onboarding_creates_connect_account_and_link(db_session, stripe_config):
    account = SimpleNamespace(id="acct_123")
    link = SimpleNamespace(url="https://connect.stripe.test/onboard", expires_at=123456)
    with patch("app.services.stripe_payout_service.stripe.Account.create", return_value=account) as create_account, \
         patch("app.services.stripe_payout_service.stripe.AccountLink.create", return_value=link) as create_link:
        result = StripePayoutService.create_onboarding_link(db_session, "payout-user-001")
    assert result["account_id"] == "acct_123"
    assert result["url"].startswith("https://")
    assert db_session.query(User).one().stripe_account_id == "acct_123"
    assert create_account.called and create_link.called


def test_withdraw_reserves_balance_until_payout_paid(db_session, stripe_config):
    db_session.query(User).one().stripe_account_id = "acct_123"
    db_session.commit()
    transfer = SimpleNamespace(id="tr_123")
    payout = SimpleNamespace(id="po_123")
    with patch("app.services.stripe_payout_service.stripe.Transfer.create", return_value=transfer), \
         patch("app.services.stripe_payout_service.stripe.Payout.create", return_value=payout):
        result = StripePayoutService.create_withdrawal(db_session, "payout-user-001", 20)
    balance = db_session.query(Balance).one()
    transaction = db_session.query(Transaction).one()
    assert result["status"] == "pending"
    assert balance.available_balance == 80
    assert balance.frozen_balance == 20
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.external_payment_id == "po_123"

    paid = {"id": "po_123", "metadata": {"transaction_id": transaction.id}}
    result = StripePayoutService.handle_payout_webhook(db_session, "payout.paid", paid)
    balance = db_session.query(Balance).one()
    assert result["status"] == "completed"
    assert balance.available_balance == 80
    assert balance.frozen_balance == 0
    assert db_session.query(Transaction).one().status == TransactionStatus.COMPLETED


def test_failed_payout_releases_reserved_balance(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_123"
    transaction = Transaction(
        id="withdraw-tx-001", user_id=user.id, type=TransactionType.WITHDRAW,
        amount=-30, status=TransactionStatus.PENDING, external_payment_id="po_456",
    )
    balance = db_session.query(Balance).one()
    balance.available_balance = 70
    balance.frozen_balance = 30
    db_session.add(transaction)
    db_session.commit()
    result = StripePayoutService.handle_payout_webhook(
        db_session, "payout.failed", {"id": "po_456", "metadata": {"transaction_id": transaction.id}}
    )
    balance = db_session.query(Balance).one()
    assert result["status"] == "failed"
    assert balance.available_balance == 100
    assert balance.frozen_balance == 0
    assert db_session.query(Transaction).one().status == TransactionStatus.FAILED
    duplicate = StripePayoutService.handle_payout_webhook(
        db_session, "payout.failed", {"id": "po_456", "metadata": {"transaction_id": transaction.id}}
    )
    assert duplicate["idempotent"] is True
    assert db_session.query(Balance).one().available_balance == 100
