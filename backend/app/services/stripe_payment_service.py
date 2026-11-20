"""Stripe 充值编排：创建 PaymentIntent，并由 Webhook 最终入账。"""

from datetime import datetime
import uuid

try:
    import stripe
except ImportError:  # Demo 模式不应因为可选支付 SDK 缺失而无法启动。
    stripe = None
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import User
from app.services.payment_service import PaymentService


class StripePaymentService:
    """把 Stripe 状态转换为本地待处理/完成/失败交易。"""

    @staticmethod
    def _require_stripe_mode() -> None:
        if settings.PAYMENT_PROVIDER.lower() != "stripe":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="真实支付尚未启用，请配置 PAYMENT_PROVIDER=stripe",
            )
        if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY.endswith("dummy"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe 密钥尚未配置",
            )
        if stripe is None:
            raise HTTPException(status_code=503, detail="Stripe SDK 未安装")

    @classmethod
    def create_charge_intent(
        cls, db: Session, user_id: str, amount: float, payment_method_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> dict:
        cls._require_stripe_mode()
        normalized = PaymentService._normalize_amount(amount)
        if normalized is None:
            raise HTTPException(status_code=400, detail="金额必须至少为 0.01")
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if not balance:
            raise HTTPException(status_code=404, detail="账户不存在")

        amount_float = float(normalized)
        transaction = None
        if idempotency_key:
            transaction = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.CHARGE,
                Transaction.idempotency_key == idempotency_key,
            ).with_for_update().first()
            if transaction and abs(transaction.amount - amount_float) > 0.000001:
                raise HTTPException(status_code=409, detail="幂等键已用于其他充值金额")
        if transaction is None:
            transaction = Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                type=TransactionType.CHARGE,
                amount=amount_float,
                status=TransactionStatus.PENDING,
                idempotency_key=idempotency_key,
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            intent_params = dict(
                amount=int(normalized * 100),
                currency=settings.STRIPE_CURRENCY,
                metadata={
                    "transaction_id": transaction.id,
                    "user_id": user_id,
                },
                idempotency_key=f"weight-bet-charge-{idempotency_key or transaction.id}",
            )
            if payment_method_id:
                intent_params.update(payment_method=payment_method_id, confirm=True)
            intent = stripe.PaymentIntent.create(**intent_params)
        except stripe.error.StripeError as error:
            transaction.status = TransactionStatus.FAILED
            db.commit()
            raise HTTPException(status_code=402, detail="Stripe 支付创建失败") from error

        transaction.external_payment_id = intent.id
        db.commit()

        return {
            "transaction_id": transaction.id,
            "payment_intent_id": intent.id,
            "client_secret": getattr(intent, "client_secret", None),
            "amount": amount_float,
            "status": intent.status,
        }

    @classmethod
    def create_setup_intent(cls, db: Session, user_id: str) -> dict:
        """创建由 Stripe PaymentSheet 收集卡信息的 SetupIntent。"""
        cls._require_stripe_mode()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            intent = stripe.SetupIntent.create(
                payment_method_types=["card"],
                metadata={"user_id": user_id},
            )
        except stripe.error.StripeError as error:
            raise HTTPException(status_code=502, detail="Stripe 支付方式初始化失败") from error
        return {
            "setup_intent_id": intent.id,
            "client_secret": getattr(intent, "client_secret", None),
            "status": intent.status,
        }

    @staticmethod
    def handle_webhook(db: Session, payload: bytes, signature: str) -> dict:
        if stripe is None:
            raise HTTPException(status_code=503, detail="Stripe SDK 未安装")
        if not settings.STRIPE_WEBHOOK_SECRET or settings.STRIPE_WEBHOOK_SECRET.endswith("dummy"):
            raise HTTPException(status_code=503, detail="Stripe Webhook 密钥尚未配置")
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as error:
            raise HTTPException(status_code=400, detail="无效的 Stripe Webhook") from error

        event_type = event["type"]
        intent = event["data"]["object"]
        if event_type in ("payout.paid", "payout.failed", "payout.canceled"):
            from app.services.stripe_payout_service import StripePayoutService
            return StripePayoutService.handle_payout_webhook(
                db, event_type, intent, connected_account=event.get("account")
            )
        if event_type in ("setup_intent.succeeded", "setup_intent.setup_failed", "setup_intent.canceled"):
            metadata = intent.get("metadata") or {}
            user_id = metadata.get("user_id")
            if not user_id:
                raise HTTPException(status_code=400, detail="Stripe SetupIntent 缺少用户标识")
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            if event_type == "setup_intent.succeeded":
                payment_method_id = intent.get("payment_method")
                if isinstance(payment_method_id, dict):
                    payment_method_id = payment_method_id.get("id")
                if not payment_method_id or not str(payment_method_id).startswith("pm_"):
                    raise HTTPException(status_code=400, detail="Stripe SetupIntent 缺少有效支付方式")
                user.payment_method_id = payment_method_id
                db.commit()
                return {"received": True, "handled": True, "status": "completed"}
            return {"received": True, "handled": True, "status": "failed"}
        if event_type not in (
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
        ):
            return {"received": True, "handled": False}

        payment_intent_id = intent.get("id")
        transaction_id = (intent.get("metadata") or {}).get("transaction_id")
        if not transaction_id:
            raise HTTPException(status_code=400, detail="Stripe PaymentIntent 缺少本地交易号")
        transaction = db.query(Transaction).filter(
            Transaction.external_payment_id == payment_intent_id
        ).with_for_update().first() if payment_intent_id else None
        if transaction is None:
            transaction = db.query(Transaction).filter(Transaction.id == transaction_id).with_for_update().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="本地交易不存在")

        metadata = intent.get("metadata") or {}
        if metadata.get("user_id") and metadata.get("user_id") != transaction.user_id:
            raise HTTPException(status_code=400, detail="Stripe 用户与本地交易不匹配")
        if transaction.external_payment_id and payment_intent_id != transaction.external_payment_id:
            raise HTTPException(status_code=400, detail="Stripe PaymentIntent 与本地交易不匹配")
        if event_type == "payment_intent.succeeded":
            actual_amount = intent.get("amount_received", intent.get("amount"))
            actual_currency = (intent.get("currency") or "").lower()
            expected_amount = int(round(transaction.amount * 100))
            if actual_amount is None or int(actual_amount) != expected_amount:
                raise HTTPException(status_code=400, detail="Stripe 支付金额与本地交易不匹配")
            if not actual_currency or actual_currency != settings.STRIPE_CURRENCY.lower():
                raise HTTPException(status_code=400, detail="Stripe 支付币种与本地配置不匹配")

        if transaction.status == TransactionStatus.COMPLETED:
            return {"received": True, "handled": True, "idempotent": True}
        if event_type == "payment_intent.payment_failed":
            transaction.status = TransactionStatus.FAILED
            db.commit()
            return {"received": True, "handled": True, "status": "failed"}

        balance = db.query(Balance).filter(Balance.user_id == transaction.user_id).with_for_update().first()
        if not balance:
            raise HTTPException(status_code=404, detail="账户不存在")
        balance.available_balance = PaymentService._add_money(
            balance.available_balance, transaction.amount
        )
        balance.updated_at = datetime.utcnow()
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.utcnow()
        db.commit()
        return {"received": True, "handled": True, "status": "completed"}
