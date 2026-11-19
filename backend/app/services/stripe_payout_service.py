"""Stripe Connect 开户、余额预留和真实出款流程。"""

from datetime import datetime
from decimal import Decimal
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
        if normalized > Decimal(str(PaymentService.MAX_WITHDRAW_AMOUNT)):
            raise HTTPException(status_code=400, detail="单次提现金额不能超过 50000")
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

    @classmethod
    def retry_pending_payout(cls, db: Session, transaction_id: str) -> dict:
        """为 Transfer 已成功但 Payout 尚未落库的交易安全重试。"""
        cls._require_stripe()
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.type == TransactionType.WITHDRAW,
            Transaction.status == TransactionStatus.PENDING,
        ).with_for_update().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="待重试提现交易不存在")
        if transaction.external_payment_id:
            return {"success": True, "status": "pending", "payout_id": transaction.external_payment_id, "idempotent": True}
        user = db.query(User).filter(User.id == transaction.user_id).first()
        if not user or not user.stripe_account_id:
            raise HTTPException(status_code=409, detail="提现账户不存在")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            if not transaction.external_transfer_id:
                transfer = stripe.Transfer.create(
                    amount=int(abs(transaction.amount) * 100),
                    currency=settings.STRIPE_CURRENCY,
                    destination=user.stripe_account_id,
                    metadata={"transaction_id": transaction.id, "user_id": transaction.user_id},
                    idempotency_key=f"weight-bet-transfer-{transaction.id}",
                )
                transaction.external_transfer_id = transfer.id
                db.commit()
            payout = stripe.Payout.create(
                amount=int(abs(transaction.amount) * 100),
                currency=settings.STRIPE_CURRENCY,
                metadata={"transaction_id": transaction.id, "user_id": transaction.user_id},
                idempotency_key=f"weight-bet-payout-{transaction.id}",
                stripe_account=user.stripe_account_id,
            )
        except stripe.error.StripeError as error:
            raise HTTPException(status_code=502, detail="Stripe Payout 重试失败") from error
        transaction.external_payment_id = payout.id
        db.commit()
        return {"success": True, "status": "pending", "payout_id": payout.id, "idempotent": False}

    @classmethod
    def reconcile_pending_payout(cls, db: Session, transaction_id: str) -> dict:
        """从 Stripe 查询已创建的 Payout，恢复丢失的 Webhook 状态。"""
        cls._require_stripe()
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.type == TransactionType.WITHDRAW,
            Transaction.status == TransactionStatus.PENDING,
        ).with_for_update().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="待对账提现交易不存在")
        if not transaction.external_payment_id:
            raise HTTPException(status_code=409, detail="提现尚未创建 Stripe Payout，请先执行重试")
        user = db.query(User).filter(User.id == transaction.user_id).first()
        if not user or not user.stripe_account_id:
            raise HTTPException(status_code=409, detail="提现账户不存在")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            payout = stripe.Payout.retrieve(
                transaction.external_payment_id,
                stripe_account=user.stripe_account_id,
            )
        except stripe.error.StripeError as error:
            raise HTTPException(status_code=502, detail="Stripe 出款状态查询失败") from error

        status_map = {
            "paid": "payout.paid",
            "failed": "payout.failed",
            "canceled": "payout.canceled",
        }
        event_type = status_map.get(payout.get("status"))
        if not event_type:
            return {
                "success": True,
                "status": "pending",
                "payout_id": transaction.external_payment_id,
                "stripe_status": payout.get("status"),
                "handled": False,
            }
        result = cls.handle_payout_webhook(
            db,
            event_type,
            dict(payout),
            connected_account=user.stripe_account_id,
        )
        return {
            "success": True,
            "status": result.get("status", "pending"),
            "payout_id": transaction.external_payment_id,
            "stripe_status": payout.get("status"),
            "handled": result.get("handled", False),
        }

    @staticmethod
    def handle_payout_webhook(
        db: Session,
        event_type: str,
        payout: dict,
        connected_account: str = None,
    ) -> dict:
        transaction_id = (payout.get("metadata") or {}).get("transaction_id")
        query = db.query(Transaction)
        transaction = query.filter(Transaction.external_payment_id == payout.get("id")).with_for_update().first()
        if transaction is None and transaction_id:
            transaction = query.filter(Transaction.id == transaction_id).with_for_update().first()
        if not transaction:
            raise HTTPException(status_code=404, detail="本地提现交易不存在")
        if transaction.status in (TransactionStatus.COMPLETED, TransactionStatus.FAILED):
            return {"received": True, "handled": True, "idempotent": True}
        payout_id = payout.get("id")
        if not payout_id:
            raise HTTPException(status_code=400, detail="Stripe 出款回调缺少 payout ID")
        # 通过 metadata 恢复本地交易时允许绑定尚未落库的 payout；
        # 已有本地 payout 则必须严格匹配，避免另一笔合法 Stripe 出款
        # 借 metadata 找到交易后改变本地资金状态。
        if transaction.external_payment_id and transaction.external_payment_id != payout_id:
            raise HTTPException(status_code=400, detail="Stripe 出款 ID 与本地提现不匹配")
        amount = abs(transaction.amount)
        user = db.query(User).filter(User.id == transaction.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        balance = db.query(Balance).filter(Balance.user_id == transaction.user_id).with_for_update().first()
        if not balance:
            raise HTTPException(status_code=404, detail="账户不存在")
        if connected_account and connected_account != user.stripe_account_id:
            raise HTTPException(status_code=400, detail="Stripe Connect 账户与本地提现不匹配")
        actual_amount = payout.get("amount")
        actual_currency = (payout.get("currency") or "").lower()
        expected_amount = int(round(amount * 100))
        if actual_amount is None or int(actual_amount) != expected_amount:
            raise HTTPException(status_code=400, detail="Stripe 出款金额与本地提现不匹配")
        if not actual_currency or actual_currency != settings.STRIPE_CURRENCY.lower():
            raise HTTPException(status_code=400, detail="Stripe 出款币种与本地配置不匹配")
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
        if not transaction.external_payment_id:
            transaction.external_payment_id = payout_id
        db.commit()
        return {"received": True, "handled": True, "status": transaction.status.value}
