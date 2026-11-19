"""平台后台管理 API。所有路由都要求数据库中的 admin 角色。"""
from datetime import datetime
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.check_in import CheckIn, ReviewStatus
from app.models.dispute import Dispute, DisputeStatus
from app.models.settlement import Settlement
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.balance import Balance
from app.models.audit_log import AuditLog
from app.schemas.admin import AdminCheckInReview, AdminDisputeUpdate, AdminUserRow
from app.services.stripe_payout_service import StripePayoutService

router = APIRouter()


@router.get("/dashboard")
def dashboard(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """返回后台首页需要的关键业务计数。"""
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "active_plans": db.query(func.count(BettingPlan.id)).filter(
            BettingPlan.status == PlanStatus.ACTIVE
        ).scalar() or 0,
        "pending_check_ins": db.query(func.count(CheckIn.id)).filter(
            CheckIn.review_status == ReviewStatus.PENDING
        ).scalar() or 0,
        "pending_disputes": db.query(func.count(Dispute.id)).filter(
            Dispute.status.in_([DisputeStatus.PENDING, DisputeStatus.UNDER_REVIEW])
        ).scalar() or 0,
        "settlements": db.query(func.count(Settlement.id)).scalar() or 0,
        "pending_payouts": db.query(func.count(Transaction.id)).filter(
            Transaction.type == TransactionType.WITHDRAW,
            Transaction.status == TransactionStatus.PENDING,
            Transaction.external_payment_id.is_(None),
        ).scalar() or 0,
        "updated_at": datetime.utcnow(),
    }


@router.get("/users", response_model=List[AdminUserRow])
def list_users(
    q: Optional[str] = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User).order_by(User.created_at.desc())
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(User.email.ilike(term), User.nickname.ilike(term)))
    return query.offset(offset).limit(limit).all()


@router.get("/plans")
def list_plans(
    plan_status: Optional[PlanStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(BettingPlan).order_by(BettingPlan.created_at.desc())
    if plan_status:
        query = query.filter(BettingPlan.status == plan_status)
    plans = query.offset(offset).limit(limit).all()
    return [
        {
            "id": plan.id,
            "status": plan.status.value,
            "bet_amount": plan.bet_amount,
            "creator_id": plan.creator_id,
            "participant_id": plan.participant_id,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "created_at": plan.created_at,
        }
        for plan in plans
    ]


@router.get("/check-ins/pending")
def list_pending_check_ins(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    records = db.query(CheckIn).filter(
        CheckIn.review_status == ReviewStatus.PENDING
    ).order_by(CheckIn.check_in_date.asc()).offset(offset).limit(limit).all()
    return [
        {
            "id": item.id,
            "plan_id": item.plan_id,
            "user_id": item.user_id,
            "weight": item.weight,
            "check_in_date": item.check_in_date,
            "photo_url": item.photo_url,
            "note": item.note,
            "review_status": item.review_status.value,
        }
        for item in records
    ]


@router.patch("/check-ins/{check_in_id}/review")
def review_check_in(
    check_in_id: str,
    request: AdminCheckInReview,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    record = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡记录不存在")
    if record.review_status != ReviewStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="只有待审核打卡可以处理"
        )
    record.review_status = request.review_status
    record.reviewer_id = admin.id
    record.review_comment = request.review_comment
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        user_id=admin.id,
        action="admin.review_check_in",
        resource_type="check_in",
        resource_id=check_in_id,
        details={"review_status": request.review_status.value},
    ))
    db.commit()
    db.refresh(record)
    return {"id": record.id, "review_status": record.review_status.value}


@router.get("/disputes")
def list_disputes(
    dispute_status: Optional[DisputeStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Dispute).order_by(Dispute.created_at.desc())
    if dispute_status:
        query = query.filter(Dispute.status == dispute_status)
    records = query.offset(offset).limit(limit).all()
    return [
        {
            "id": item.id,
            "settlement_id": item.settlement_id,
            "user_id": item.user_id,
            "reason": item.reason,
            "description": item.description,
            "status": item.status.value,
            "admin_notes": item.admin_notes,
            "created_at": item.created_at,
            "resolved_at": item.resolved_at,
        }
        for item in records
    ]


@router.patch("/disputes/{dispute_id}")
def update_dispute(
    dispute_id: str,
    request: AdminDisputeUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="争议记录不存在")
    allowed_transitions = {
        DisputeStatus.PENDING: {DisputeStatus.UNDER_REVIEW, DisputeStatus.RESOLVED, DisputeStatus.REJECTED},
        DisputeStatus.UNDER_REVIEW: {DisputeStatus.RESOLVED, DisputeStatus.REJECTED},
        DisputeStatus.RESOLVED: set(),
        DisputeStatus.REJECTED: set(),
    }
    if request.status not in allowed_transitions[dispute.status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"争议状态不能从 {dispute.status.value} 变更为 {request.status.value}"
        )
    dispute.status = request.status
    dispute.admin_notes = request.admin_notes
    dispute.resolved_by = admin.id if request.status in (DisputeStatus.RESOLVED, DisputeStatus.REJECTED) else None
    dispute.resolved_at = datetime.utcnow() if dispute.resolved_by else None
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        user_id=admin.id,
        action="admin.update_dispute",
        resource_type="dispute",
        resource_id=dispute_id,
        details={"status": request.status.value},
    ))
    db.commit()
    db.refresh(dispute)
    return {"id": dispute.id, "status": dispute.status.value, "resolved_by": dispute.resolved_by}


@router.get("/settlements")
def list_settlements(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    records = db.query(Settlement).order_by(Settlement.settlement_date.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": item.id,
            "plan_id": item.plan_id,
            "creator_amount": item.creator_amount,
            "participant_amount": item.participant_amount,
            "platform_fee": item.platform_fee,
            "in_arbitration": item.in_arbitration,
            "settlement_date": item.settlement_date,
        }
        for item in records
    ]


@router.get("/transactions")
def list_transactions(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    records = db.query(Transaction).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "type": item.type.value,
            "amount": item.amount,
            "status": item.status.value,
            "related_plan_id": item.related_plan_id,
            "related_settlement_id": item.related_settlement_id,
            "external_payment_id": item.external_payment_id,
            "external_transfer_id": item.external_transfer_id,
            "retryable_payout": (
                item.type == TransactionType.WITHDRAW
                and item.status == TransactionStatus.PENDING
                and item.external_payment_id is None
            ),
            "needs_transfer_recovery": (
                item.type == TransactionType.WITHDRAW
                and item.status == TransactionStatus.PENDING
                and item.external_transfer_id is None
                and item.external_payment_id is None
            ),
            "created_at": item.created_at,
        }
        for item in records
    ]


@router.get("/payouts/pending")
def list_pending_payouts(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """列出需要 Stripe Transfer/Payout 恢复的待处理提现。"""
    records = db.query(Transaction).filter(
        Transaction.type == TransactionType.WITHDRAW,
        Transaction.status == TransactionStatus.PENDING,
        Transaction.external_payment_id.is_(None),
    ).order_by(Transaction.created_at.asc()).offset(offset).limit(limit).all()
    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "amount": abs(item.amount),
            "external_transfer_id": item.external_transfer_id,
            "needs_transfer_recovery": item.external_transfer_id is None,
            "created_at": item.created_at,
        }
        for item in records
    ]


@router.get("/balances")
def list_balances(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    records = db.query(Balance).order_by(Balance.updated_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "user_id": item.user_id,
            "available_balance": item.available_balance,
            "frozen_balance": item.frozen_balance,
            "updated_at": item.updated_at,
        }
        for item in records
    ]


@router.get("/audit-logs")
def list_audit_logs(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    records = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "action": item.action,
            "resource_type": item.resource_type,
            "resource_id": item.resource_id,
            "details": item.details,
            "created_at": item.created_at,
        }
        for item in records
    ]


@router.post("/payouts/{transaction_id}/retry")
def retry_payout(
    transaction_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """重试 Transfer 已成功但 Payout 尚未创建的提现。"""
    result = StripePayoutService.retry_pending_payout(db, transaction_id)
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        user_id=admin.id,
        action="retry_payout",
        resource_type="transaction",
        resource_id=transaction_id,
        details=result,
    ))
    db.commit()
    return result
