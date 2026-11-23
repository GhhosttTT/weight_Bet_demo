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
    account = SimpleNamespace(details_submitted=True, payouts_enabled=True)
    with patch("app.services.stripe_payout_service.stripe.Account.retrieve", return_value=account), \
         patch("app.services.stripe_payout_service.stripe.Transfer.create", return_value=transfer), \
         patch("app.services.stripe_payout_service.stripe.Payout.create", return_value=payout):
        result = StripePayoutService.create_withdrawal(db_session, "payout-user-001", 20)
    balance = db_session.query(Balance).one()
    transaction = db_session.query(Transaction).one()
    assert result["status"] == "pending"
    assert balance.available_balance == 80
    assert balance.frozen_balance == 20
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.external_payment_id == "po_123"

    paid = {"id": "po_123", "amount": 2000, "currency": "cny", "metadata": {"transaction_id": transaction.id}}
    result = StripePayoutService.handle_payout_webhook(db_session, "payout.paid", paid)
    balance = db_session.query(Balance).one()
    assert result["status"] == "completed"
    assert balance.available_balance == 80
    assert balance.frozen_balance == 0
    assert db_session.query(Transaction).one().status == TransactionStatus.COMPLETED


def test_withdraw_rejects_connect_account_without_payout_capability(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_incomplete"
    db_session.commit()
    account = SimpleNamespace(details_submitted=True, payouts_enabled=False)
    with patch("app.services.stripe_payout_service.stripe.Account.retrieve", return_value=account), \
         pytest.raises(HTTPException) as error:
        StripePayoutService.create_withdrawal(db_session, user.id, 20)
    assert error.value.status_code == 409
    assert "出款资格" in error.value.detail
    balance = db_session.query(Balance).one()
    assert balance.available_balance == 100
    assert balance.frozen_balance == 0


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
        db_session, "payout.failed", {"id": "po_456", "amount": 3000, "currency": "cny", "metadata": {"transaction_id": transaction.id}}
    )
    balance = db_session.query(Balance).one()
    assert result["status"] == "failed"
    assert balance.available_balance == 100
    assert balance.frozen_balance == 0
    assert db_session.query(Transaction).one().status == TransactionStatus.FAILED
    duplicate = StripePayoutService.handle_payout_webhook(
        db_session, "payout.failed", {"id": "po_456", "amount": 3000, "currency": "cny", "metadata": {"transaction_id": transaction.id}}
    )
    assert duplicate["idempotent"] is True
    assert db_session.query(Balance).one().available_balance == 100


def test_payout_webhook_rejects_id_mismatch(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_123"
    transaction = Transaction(
        id="withdraw-tx-mismatch", user_id=user.id, type=TransactionType.WITHDRAW,
        amount=-30, status=TransactionStatus.PENDING, external_payment_id="po_expected",
    )
    balance = db_session.query(Balance).one()
    balance.available_balance = 70
    balance.frozen_balance = 30
    db_session.add(transaction)
    db_session.commit()

    with pytest.raises(HTTPException) as error:
        StripePayoutService.handle_payout_webhook(
            db_session,
            "payout.paid",
            {"id": "po_other", "amount": 3000, "currency": "cny", "metadata": {"transaction_id": transaction.id}},
        )
    assert error.value.detail == "Stripe 出款 ID 与本地提现不匹配"
    db_session.refresh(transaction)
    db_session.refresh(balance)
    assert transaction.status == TransactionStatus.PENDING
    assert balance.available_balance == 70
    assert balance.frozen_balance == 30


def test_payout_webhook_rejects_non_withdraw_transaction_without_changing_balance(db_session, stripe_config):
    transaction = Transaction(
        id="charge-as-payout", user_id="payout-user-001", type=TransactionType.CHARGE,
        amount=30, status=TransactionStatus.PENDING, external_payment_id="po_wrong_type",
    )
    db_session.add(transaction)
    db_session.commit()
    with pytest.raises(HTTPException) as error:
        StripePayoutService.handle_payout_webhook(
            db_session,
            "payout.paid",
            {"id": "po_wrong_type", "amount": 3000, "currency": "cny",
             "metadata": {"transaction_id": transaction.id}},
        )
    assert error.value.status_code == 400
    db_session.refresh(transaction)
    assert transaction.status == TransactionStatus.PENDING
    balance = db_session.query(Balance).one()
    assert balance.available_balance == 100
    assert balance.frozen_balance == 0


def test_retry_pending_payout_uses_same_idempotency_key(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_retry"
    transaction = Transaction(
        id="retry-tx-001", user_id=user.id, type=TransactionType.WITHDRAW,
        amount=-15, status=TransactionStatus.PENDING, external_transfer_id="tr_retry",
    )
    db_session.add(transaction)
    db_session.commit()
    payout = SimpleNamespace(id="po_retry")
    with patch("app.services.stripe_payout_service.stripe.Payout.create", return_value=payout) as create:
        result = StripePayoutService.retry_pending_payout(db_session, transaction.id)
    assert result["payout_id"] == "po_retry"
    assert db_session.query(Transaction).one().external_payment_id == "po_retry"
    assert create.call_args[1]["idempotency_key"] == "weight-bet-payout-retry-tx-001"


def test_retry_pending_payout_recovers_missing_transfer(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_recover"
    transaction = Transaction(
        id="recover-tx-001", user_id=user.id, type=TransactionType.WITHDRAW,
        amount=-15, status=TransactionStatus.PENDING,
    )
    db_session.add(transaction)
    db_session.commit()
    transfer = SimpleNamespace(id="tr_recovered")
    payout = SimpleNamespace(id="po_recovered")
    with patch("app.services.stripe_payout_service.stripe.Transfer.create", return_value=transfer) as create_transfer, \
         patch("app.services.stripe_payout_service.stripe.Payout.create", return_value=payout) as create_payout:
        result = StripePayoutService.retry_pending_payout(db_session, transaction.id)
    stored = db_session.query(Transaction).one()
    assert result["payout_id"] == "po_recovered"
    assert stored.external_transfer_id == "tr_recovered"
    assert stored.external_payment_id == "po_recovered"
    assert create_transfer.call_args[1]["idempotency_key"] == "weight-bet-transfer-recover-tx-001"
    assert create_payout.call_args[1]["idempotency_key"] == "weight-bet-payout-recover-tx-001"


@pytest.mark.parametrize("amount, expected_cents", [
    (-0.01, 1),
    (-0.29, 29),
    (-10.29, 1029),
    (-50000.00, 5000000),
])
def test_retry_pending_payout_uses_decimal_minor_units(db_session, stripe_config, amount, expected_cents):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_decimal"
    transaction = Transaction(
        id=f"retry-decimal-{str(abs(amount)).replace('.', '-')}", user_id=user.id,
        type=TransactionType.WITHDRAW, amount=amount,
        status=TransactionStatus.PENDING, external_transfer_id="tr_decimal",
    )
    db_session.add(transaction)
    db_session.commit()
    payout = SimpleNamespace(id="po_decimal")
    with patch("app.services.stripe_payout_service.stripe.Payout.create", return_value=payout) as create:
        StripePayoutService.retry_pending_payout(db_session, transaction.id)
    assert create.call_args[1]["amount"] == expected_cents


def test_payout_webhook_validates_decimal_minor_units(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_decimal_webhook"
    transaction = Transaction(
        id="webhook-decimal", user_id=user.id, type=TransactionType.WITHDRAW,
        amount=-0.29, status=TransactionStatus.PENDING, external_payment_id="po_decimal_webhook",
    )
    balance = db_session.query(Balance).one()
    balance.available_balance = 99.71
    balance.frozen_balance = 0.29
    db_session.add(transaction)
    db_session.commit()
    result = StripePayoutService.handle_payout_webhook(
        db_session, "payout.paid",
        {"id": "po_decimal_webhook", "amount": 29, "currency": "cny",
         "metadata": {"transaction_id": transaction.id}},
    )
    assert result["status"] == "completed"
    assert db_session.query(Balance).one().frozen_balance == 0


def test_reconcile_pending_payout_applies_stripe_paid_status(db_session, stripe_config):
    user = db_session.query(User).one()
    user.stripe_account_id = "acct_reconcile"
    transaction = Transaction(
        id="reconcile-tx-001", user_id=user.id, type=TransactionType.WITHDRAW,
        amount=-20, status=TransactionStatus.PENDING, external_payment_id="po_reconcile",
    )
    balance = db_session.query(Balance).one()
    balance.available_balance = 80
    balance.frozen_balance = 20
    db_session.add(transaction)
    db_session.commit()

    payout = {
        "id": "po_reconcile",
        "status": "paid",
        "amount": 2000,
        "currency": "cny",
        "metadata": {"transaction_id": transaction.id, "user_id": user.id},
    }
    with patch("app.services.stripe_payout_service.stripe.Payout.retrieve", return_value=payout) as retrieve:
        result = StripePayoutService.reconcile_pending_payout(db_session, transaction.id)

    retrieve.assert_called_once_with("po_reconcile", stripe_account="acct_reconcile")
    assert result["status"] == "completed"
    assert db_session.query(Transaction).one().status == TransactionStatus.COMPLETED
    assert db_session.query(Balance).one().frozen_balance == 0
