"""平台后台管理 API。所有路由都要求数据库中的 admin 角色。"""
from datetime import datetime
from typing import List, Optional
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
from app.schemas.admin import AdminCheckInReview, AdminDisputeUpdate, AdminUserRow

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
    record.review_status = request.review_status
    record.reviewer_id = admin.id
    record.review_comment = request.review_comment
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
    dispute.status = request.status
    dispute.admin_notes = request.admin_notes
    dispute.resolved_by = admin.id if request.status in (DisputeStatus.RESOLVED, DisputeStatus.REJECTED) else None
    dispute.resolved_at = datetime.utcnow() if dispute.resolved_by else None
    db.commit()
    db.refresh(dispute)
    return {"id": dispute.id, "status": dispute.status.value, "resolved_by": dispute.resolved_by}
