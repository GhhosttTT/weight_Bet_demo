"""Stripe PaymentIntent 与 Webhook 入账测试。"""

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
from app.services.stripe_payment_service import StripePaymentService
from app.api.payments import withdraw, charge
from app.schemas.payment import ChargeRequest, WithdrawRequest


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    user = User(
        id="stripe-user-001", email="stripe@example.com", password_hash="hash",
        nickname="Stripe User", gender=Gender.OTHER, age=30, height=170, current_weight=70,
        payment_method_id="pm_card_visa",
    )
    db.add(user)
    db.add(Balance(user_id=user.id, available_balance=0, frozen_balance=0))
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_intent_requires_stripe_mode(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "demo")
    with pytest.raises(HTTPException) as error:
        StripePaymentService.create_charge_intent(db_session, "stripe-user-001", 10, "pm_card_visa")
    assert error.value.status_code == 503


def test_create_intent_creates_pending_transaction(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_realistic")
    fake_intent = type("Intent", (), {
        "id": "pi_123", "client_secret": "secret_123", "status": "requires_action"
    })()
    with patch("app.services.stripe_payment_service.stripe.PaymentIntent.create", return_value=fake_intent) as create:
        result = StripePaymentService.create_charge_intent(
            db_session, "stripe-user-001", 10.005
        )
    assert result["status"] == "requires_action"
    transaction = db_session.query(Transaction).one()
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.amount == 10.01
    assert create.call_args[1]["amount"] == 1001
    assert "payment_method" not in create.call_args[1]


def test_webhook_success_credits_once(db_session, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_realistic")
    transaction = Transaction(
        id="charge-tx-001", user_id="stripe-user-001", type=TransactionType.CHARGE,
        amount=20.0, status=TransactionStatus.PENDING,
    )
    db_session.add(transaction)
    db_session.commit()
    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": {"metadata": {"transaction_id": transaction.id}}},
    }
    with patch("app.services.stripe_payment_service.stripe.Webhook.construct_event", return_value=event):
        first = StripePaymentService.handle_webhook(db_session, b"payload", "signature")
        second = StripePaymentService.handle_webhook(db_session, b"payload", "signature")
    balance = db_session.query(Balance).one()
    assert first["status"] == "completed"
    assert second["idempotent"] is True
    assert balance.available_balance == 20.0
    assert db_session.query(Transaction).one().status == TransactionStatus.COMPLETED


def test_webhook_failure_does_not_credit(db_session, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_realistic")
    transaction = Transaction(
        id="charge-tx-002", user_id="stripe-user-001", type=TransactionType.CHARGE,
        amount=20.0, status=TransactionStatus.PENDING,
    )
    db_session.add(transaction)
    db_session.commit()
    event = {
        "type": "payment_intent.payment_failed",
        "data": {"object": {"metadata": {"transaction_id": transaction.id}}},
    }
    with patch("app.services.stripe_payment_service.stripe.Webhook.construct_event", return_value=event):
        result = StripePaymentService.handle_webhook(db_session, b"payload", "signature")
    assert result["status"] == "failed"
    assert db_session.query(Balance).one().available_balance == 0


def test_stripe_mode_blocks_legacy_direct_money_endpoints(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    with pytest.raises(HTTPException) as withdraw_error:
        withdraw(WithdrawRequest(amount=1, payment_method_id="pm_card_visa"), "stripe-user-001", db_session)
    with pytest.raises(HTTPException) as charge_error:
        charge(ChargeRequest(amount=1, paymentMethodId="pm_card_visa"), "stripe-user-001", db_session)
    assert withdraw_error.value.status_code == 503
    assert charge_error.value.status_code == 410
