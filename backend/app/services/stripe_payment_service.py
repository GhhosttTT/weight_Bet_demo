"""Stripe 充值编排：创建 PaymentIntent，并由 Webhook 最终入账。"""

from datetime import datetime
import uuid

try:
    import stripe
except ImportError:  # Demo 模式不应因为可选支付 SDK 缺失而无法启动。
    stripe = None
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionStatus, TransactionType
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
        cls, db: Session, user_id: str, amount: float, payment_method_id: str
    ) -> dict:
        cls._require_stripe_mode()
        normalized = PaymentService._normalize_amount(amount)
        if normalized is None:
            raise HTTPException(status_code=400, detail="金额必须至少为 0.01")
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if not balance:
            raise HTTPException(status_code=404, detail="账户不存在")

        amount_float = float(normalized)
        transaction = Transaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=TransactionType.CHARGE,
            amount=amount_float,
            status=TransactionStatus.PENDING,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(normalized * 100),
                currency=settings.STRIPE_CURRENCY,
                payment_method=payment_method_id,
                confirm=True,
                metadata={
                    "transaction_id": transaction.id,
                    "user_id": user_id,
                },
                idempotency_key=f"weight-bet-charge-{transaction.id}",
            )
        except stripe.error.StripeError as error:
            transaction.status = TransactionStatus.FAILED
            db.commit()
            raise HTTPException(status_code=402, detail="Stripe 支付创建失败") from error

        return {
            "transaction_id": transaction.id,
            "payment_intent_id": intent.id,
            "client_secret": getattr(intent, "client_secret", None),
            "amount": amount_float,
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
        if event_type not in (
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
        ):
            return {"received": True, "handled": False}

        transaction_id = (intent.get("metadata") or {}).get("transaction_id")
        if not transaction_id:
            raise HTTPException(status_code=400, detail="Stripe PaymentIntent 缺少本地交易号")
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).with_for_update().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="本地交易不存在")

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
