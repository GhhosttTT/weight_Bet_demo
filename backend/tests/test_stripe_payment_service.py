"""Stripe PaymentIntent 与 Webhook 入账测试。"""

from unittest.mock import patch
import hashlib
import hmac
import json
import time

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
from app.services.payment_service import PaymentService
from app.api.payments import withdraw, charge
from app.schemas.payment import ChargeRequest, WithdrawRequest
from app.schemas.payment import ChargeIntentRequest


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


def test_transaction_status_is_isolated_to_owner(db_session):
    transaction = Transaction(
        id="charge-status-001",
        user_id="stripe-user-001",
        type=TransactionType.CHARGE,
        amount=25,
        status=TransactionStatus.PENDING,
    )
    db_session.add(transaction)
    db_session.commit()

    assert PaymentService.get_transaction(db_session, "stripe-user-001", transaction.id) is not None
    assert PaymentService.get_transaction(db_session, "another-user", transaction.id) is None


def test_charge_intent_requires_client_idempotency_key():
    with pytest.raises(ValueError):
        ChargeIntentRequest(amount=10)


def test_create_intent_creates_pending_transaction(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_realistic")
    fake_intent = type("Intent", (), {
        "id": "pi_123", "client_secret": "secret_123", "status": "requires_action"
    })()
    with patch("app.services.stripe_payment_service.stripe.PaymentIntent.create", return_value=fake_intent) as create:
        result = StripePaymentService.create_charge_intent(
            db_session, "stripe-user-001", 10.005, idempotency_key="request-key-100005"
        )
    assert result["status"] == "requires_action"
    transaction = db_session.query(Transaction).one()
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.amount == 10.01
    assert create.call_args[1]["amount"] == 1001
    assert "payment_method" not in create.call_args[1]


def test_create_intent_reuses_client_idempotency_key(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_realistic")
    fake_intent = type("Intent", (), {
        "id": "pi_idempotent", "client_secret": "secret_idempotent", "status": "requires_action"
    })()
    with patch("app.services.stripe_payment_service.stripe.PaymentIntent.create", return_value=fake_intent) as create:
        first = StripePaymentService.create_charge_intent(
            db_session, "stripe-user-001", 20, idempotency_key="request-key-123456"
        )
        second = StripePaymentService.create_charge_intent(
            db_session, "stripe-user-001", 20, idempotency_key="request-key-123456"
        )
    assert first["transaction_id"] == second["transaction_id"]
    assert first["payment_intent_id"] == second["payment_intent_id"]
    assert db_session.query(Transaction).count() == 1
    assert create.call_args[1]["idempotency_key"] == "weight-bet-charge-request-key-123456"


def test_create_intent_rejects_idempotency_key_used_by_another_user(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_realistic")
    other_user = User(
        id="stripe-user-002", email="stripe2@example.com", password_hash="hash",
        nickname="Stripe User 2", gender=Gender.OTHER, age=30, height=170,
        current_weight=70,
    )
    db_session.add(other_user)
    db_session.add(Balance(user_id=other_user.id, available_balance=0, frozen_balance=0))
    db_session.commit()
    fake_intent = type("Intent", (), {
        "id": "pi_first", "client_secret": "secret_first", "status": "requires_action"
    })()
    with patch("app.services.stripe_payment_service.stripe.PaymentIntent.create", return_value=fake_intent) as create:
        StripePaymentService.create_charge_intent(
            db_session, "stripe-user-001", 20, idempotency_key="request-key-shared"
        )
        with pytest.raises(HTTPException) as error:
            StripePaymentService.create_charge_intent(
                db_session, "stripe-user-002", 20, idempotency_key="request-key-shared"
            )
    assert error.value.status_code == 409
    assert "其他用户" in error.value.detail
    assert create.call_count == 1
    assert db_session.query(Transaction).count() == 1


def test_create_setup_intent_does_not_receive_raw_card_data(db_session, monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_realistic")
    fake_intent = type("SetupIntent", (), {
        "id": "seti_123", "client_secret": "seti_secret_123", "status": "requires_payment_method"
    })()
    with patch("app.services.stripe_payment_service.stripe.SetupIntent.create", return_value=fake_intent) as create:
        result = StripePaymentService.create_setup_intent(db_session, "stripe-user-001")
    assert result == {
        "setup_intent_id": "seti_123",
        "client_secret": "seti_secret_123",
        "status": "requires_payment_method",
    }
    assert create.call_args[1]["payment_method_types"] == ["card"]
    assert "card_number" not in create.call_args[1]
    assert "cvv" not in create.call_args[1]


def test_setup_intent_webhook_binds_verified_stripe_payment_method(db_session, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_realistic")
    event = {
        "type": "setup_intent.succeeded",
        "data": {"object": {
            "id": "seti_123",
            "payment_method": "pm_real_123",
            "metadata": {"user_id": "stripe-user-001"},
        }},
    }
    with patch("app.services.stripe_payment_service.stripe.Webhook.construct_event", return_value=event):
        result = StripePaymentService.handle_webhook(db_session, b"payload", "signature")
    assert result["status"] == "completed"
    assert db_session.query(User).one().payment_method_id == "pm_real_123"


def test_webhook_rejects_amount_mismatch(db_session, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_realistic")
    transaction = Transaction(
        id="charge-tx-mismatch", user_id="stripe-user-001", type=TransactionType.CHARGE,
        amount=20.0, status=TransactionStatus.PENDING, external_payment_id="pi_mismatch",
    )
    db_session.add(transaction)
    db_session.commit()
    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": {
            "id": "pi_mismatch",
            "metadata": {"transaction_id": transaction.id, "user_id": transaction.user_id},
            "amount_received": 1900,
            "currency": "cny",
        }},
    }
    with patch("app.services.stripe_payment_service.stripe.Webhook.construct_event", return_value=event):
        with pytest.raises(HTTPException) as error:
            StripePaymentService.handle_webhook(db_session, b"payload", "signature")
    assert error.value.status_code == 400


def test_webhook_success_credits_once(db_session, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_realistic")
    transaction = Transaction(
        id="charge-tx-001", user_id="stripe-user-001", type=TransactionType.CHARGE,
        amount=20.0, status=TransactionStatus.PENDING, external_payment_id="pi_charge_001",
    )
    db_session.add(transaction)
    db_session.commit()
    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": {
            "id": "pi_charge_001",
            "metadata": {"transaction_id": transaction.id, "user_id": transaction.user_id},
            "amount_received": 2000,
            "currency": "cny",
        }},
    }
    with patch("app.services.stripe_payment_service.stripe.Webhook.construct_event", return_value=event):
        first = StripePaymentService.handle_webhook(db_session, b"payload", "signature")
        second = StripePaymentService.handle_webhook(db_session, b"payload", "signature")
    balance = db_session.query(Balance).one()
    assert first["status"] == "completed"
    assert second["idempotent"] is True
    assert balance.available_balance == 20.0
    assert db_session.query(Transaction).one().status == TransactionStatus.COMPLETED


def test_webhook_accepts_real_stripe_signature_and_credits_once(db_session, monkeypatch):
    """使用 Stripe SDK 的真实签名格式，验证 Webhook 验签与业务处理的连接。"""
    secret = "whsec_realistic"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    transaction = Transaction(
        id="charge-tx-real-signature", user_id="stripe-user-001", type=TransactionType.CHARGE,
        amount=20.0, status=TransactionStatus.PENDING, external_payment_id="pi_real_signature",
    )
    db_session.add(transaction)
    db_session.commit()
    payload = json.dumps({
        "id": "evt_real_signature",
        "object": "event",
        "type": "payment_intent.succeeded",
        "data": {"object": {
            "id": "pi_real_signature",
            "metadata": {"transaction_id": transaction.id, "user_id": transaction.user_id},
            "amount_received": 2000,
            "currency": "cny",
        }},
    }, separators=(",", ":")).encode()
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.".encode() + payload
    digest = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    signature = f"t={timestamp},v1={digest}"

    result = StripePaymentService.handle_webhook(db_session, payload, signature)

    assert result["status"] == "completed"
    assert db_session.query(Balance).one().available_balance == 20.0


def test_webhook_failure_does_not_credit(db_session, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_realistic")
    transaction = Transaction(
        id="charge-tx-002", user_id="stripe-user-001", type=TransactionType.CHARGE,
        amount=20.0, status=TransactionStatus.PENDING, external_payment_id="pi_charge_002",
    )
    db_session.add(transaction)
    db_session.commit()
    event = {
        "type": "payment_intent.payment_failed",
        "data": {"object": {
            "id": "pi_charge_002",
            "metadata": {"transaction_id": transaction.id, "user_id": transaction.user_id},
        }},
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
