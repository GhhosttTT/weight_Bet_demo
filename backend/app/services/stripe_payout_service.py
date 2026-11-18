"""Stripe Connect 开户、余额预留和真实出款流程。"""

from datetime import datetime
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import User
from app.services.payment_service import PaymentService
from app.services.stripe_payment_service import StripePaymentService, stripe


class StripePayoutService:
    """Connect Express 账户与 Payout 状态编排。"""

    @staticmethod
    def _require_stripe() -> None:
        StripePaymentService._require_stripe_mode()

    @classmethod
    def create_onboarding_link(cls, db: Session, user_id: str) -> dict:
        cls._require_stripe()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            if not user.stripe_account_id:
                account = stripe.Account.create(
                    type="express",
                    country=settings.STRIPE_CONNECT_COUNTRY,
                    email=user.email,
                    capabilities={"transfers": {"requested": True}},
                    metadata={"user_id": user.id},
                )
                user.stripe_account_id = account.id
                db.commit()
            link = stripe.AccountLink.create(
                account=user.stripe_account_id,
                refresh_url=settings.STRIPE_CONNECT_REFRESH_URL,
                return_url=settings.STRIPE_CONNECT_RETURN_URL,
                type="account_onboarding",
            )
        except stripe.error.StripeError as error:
            db.rollback()
            raise HTTPException(status_code=502, detail="Stripe 开户链接创建失败") from error
        return {"account_id": user.stripe_account_id, "url": link.url, "expires_at": link.expires_at}

    @classmethod
    def create_withdrawal(cls, db: Session, user_id: str, amount: float) -> dict:
        cls._require_stripe()
        normalized = PaymentService._normalize_amount(amount)
        if normalized is None:
            raise HTTPException(status_code=400, detail="金额必须至少为 0.01")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.stripe_account_id:
            raise HTTPException(status_code=409, detail="请先完成 Stripe Connect 提现账户认证")
        balance = db.query(Balance).filter(Balance.user_id == user_id).with_for_update().first()
        if not balance:
            raise HTTPException(status_code=404, detail="账户不存在")
        amount_float = float(normalized)
        if balance.available_balance < amount_float:
            raise HTTPException(status_code=400, detail="余额不足")
        pending = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.WITHDRAW,
            Transaction.status == TransactionStatus.PENDING,
        ).first()
        if pending:
            raise HTTPException(status_code=409, detail="已有提现处理中")

        transaction = Transaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=TransactionType.WITHDRAW,
            amount=-amount_float,
            status=TransactionStatus.PENDING,
        )
        balance.available_balance = PaymentService._subtract_money(balance.available_balance, amount_float)
        balance.frozen_balance = PaymentService._add_money(balance.frozen_balance, amount_float)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        cents = int(normalized * 100)
        try:
            transfer = stripe.Transfer.create(
                amount=cents,
                currency=settings.STRIPE_CURRENCY,
                destination=user.stripe_account_id,
                metadata={"transaction_id": transaction.id, "user_id": user_id},
                idempotency_key=f"weight-bet-transfer-{transaction.id}",
            )
            # 先持久化 Transfer ID。若后续 Payout 调用失败，保留 pending
            # 状态并依靠对账/重试处理，不能释放已经转出到 Connect 账户的资金。
            transaction.external_transfer_id = transfer.id
            db.commit()
            payout = stripe.Payout.create(
                amount=cents,
                currency=settings.STRIPE_CURRENCY,
                metadata={"transaction_id": transaction.id, "user_id": user_id},
                idempotency_key=f"weight-bet-payout-{transaction.id}",
                stripe_account=user.stripe_account_id,
            )
            transaction.external_payment_id = payout.id
            db.commit()
        except stripe.error.StripeError as error:
            # Transfer 尚未成功时可以安全释放预留余额；已转出时保留 pending，交由 webhook/对账处理。
            if "transfer" not in locals():
                balance.available_balance = PaymentService._add_money(balance.available_balance, amount_float)
                balance.frozen_balance = PaymentService._subtract_money(balance.frozen_balance, amount_float)
                transaction.status = TransactionStatus.FAILED
                db.commit()
            raise HTTPException(status_code=502, detail="Stripe 出款创建失败") from error
        return {
            "success": True,
            "transaction_id": transaction.id,
            "amount": amount_float,
            "message": "提现申请已提交，等待 Stripe 出款确认",
            "status": "pending",
            "payout_id": transaction.external_payment_id,
        }

    @staticmethod
    def handle_payout_webhook(db: Session, event_type: str, payout: dict) -> dict:
        transaction_id = (payout.get("metadata") or {}).get("transaction_id")
        query = db.query(Transaction)
        transaction = query.filter(Transaction.external_payment_id == payout.get("id")).with_for_update().first()
        if transaction is None and transaction_id:
            transaction = query.filter(Transaction.id == transaction_id).with_for_update().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="本地提现交易不存在")
        if transaction.status == TransactionStatus.COMPLETED:
            return {"received": True, "handled": True, "idempotent": True}
        amount = abs(transaction.amount)
        balance = db.query(Balance).filter(Balance.user_id == transaction.user_id).with_for_update().first()
        if not balance:
            raise HTTPException(status_code=404, detail="账户不存在")
        if event_type == "payout.paid":
            balance.frozen_balance = PaymentService._subtract_money(balance.frozen_balance, amount)
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()
        elif event_type in ("payout.failed", "payout.canceled"):
            balance.frozen_balance = PaymentService._subtract_money(balance.frozen_balance, amount)
            balance.available_balance = PaymentService._add_money(balance.available_balance, amount)
            transaction.status = TransactionStatus.FAILED
        else:
            return {"received": True, "handled": False}
        db.commit()
        return {"received": True, "handled": True, "status": transaction.status.value}
