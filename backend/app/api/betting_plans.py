"""
对赌计划 API 路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.betting_plan import CreatePlanRequest, AcceptPlanRequest, PlanResponse, AbandonPlanRequest, AbandonPlanResponse
from app.services.betting_plan_service import BettingPlanService
from app.middleware.auth import get_current_user_id
from app.models.betting_plan import PlanStatus, BettingPlan
from pydantic import BaseModel

router = APIRouter()


@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(
    request: CreatePlanRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建对赌计划
    
    - **bet_amount**: 赌金金额
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **initial_weight**: 初始体重
    - **target_weight**: 目标体重
    - **description**: 计划描述 (可选)
    - **invitee_id**: 邀请对象 ID (可选)
    """
    return BettingPlanService.create_plan(db, current_user_id, request)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan_details(
    plan_id: str,
    db: Session = Depends(get_db)
):
    """
    获取计划详情
    
    - **plan_id**: 计划 ID
    """
    return BettingPlanService.get_plan_details(db, plan_id)


@router.post("/{plan_id}/accept", response_model=PlanResponse)
def accept_plan(
    plan_id: str,
    request: AcceptPlanRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    接受对赌计划
    
    - **plan_id**: 计划 ID
    - **initial_weight**: 参与者初始体重
    - **target_weight**: 参与者目标体重
    
    参与者接受后，计划状态仍为 pending，等待创建者确认
    """
    return BettingPlanService.accept_plan(db, plan_id, current_user_id, request)


@router.post("/{plan_id}/confirm", response_model=PlanResponse)
def confirm_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    确认对赌计划生效（创建者确认参与者的计划）
    
    - **plan_id**: 计划 ID
    
    只有创建者可以确认，确认后计划正式生效（active）
    """
    return BettingPlanService.confirm_plan(db, plan_id, current_user_id)


@router.post("/{plan_id}/reject")
def reject_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    拒绝对赌计划
    
    - **plan_id**: 计划 ID
    """
    return BettingPlanService.reject_plan(db, plan_id, current_user_id)


@router.post("/{plan_id}/cancel")
def cancel_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消对赌计划
    
    - **plan_id**: 计划 ID
    
    注意：只有创建者可以取消未生效的计划
    """
    return BettingPlanService.cancel_plan(db, plan_id, current_user_id)


@router.post("/{plan_id}/revoke")
def revoke_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    撤销对赌计划（创建者撤销待接受的计划）
    
    - **plan_id**: 计划 ID
    
    只有创建者可以撤销待接受的计划，双方冻结金额原路返还
    """
    return BettingPlanService.revoke_plan(db, plan_id, current_user_id)


@router.post("/{plan_id}/abandon")
def abandon_plan(
    plan_id: str,
    request: AbandonPlanRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    放弃对赌计划
    
    - **plan_id**: 计划 ID
    - **confirmation**: 确认标志
    
    根据计划状态处理不同的放弃逻辑：
    - pending 状态：退还创建者赌金
    - active 状态：将双方赌金转给对方（获胜方）
    """
    from app.services.plan_status_manager import PlanStatusManager
    from app.schemas.payment import AbandonResult
    
    result: AbandonResult = PlanStatusManager.abandon_plan(db, plan_id, current_user_id)
    
    # 获取更新后的计划状态
    plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
    
    return {
        "success": result.success,
        "plan_id": result.plan_id,
        "status": plan.status.value if plan else "cancelled",
        "refunded_amount": result.refunded_amount,
        "transferred_amount": result.transferred_amount,
        "message": result.message
    }


@router.get("/users/{user_id}/plans", response_model=List[PlanResponse])
def get_user_plans(
    user_id: str,
    status: Optional[PlanStatus] = Query(None, description="计划状态筛选"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的计划列表
    
    - **user_id**: 用户 ID
    - **status**: 状态筛选 (可选)
    - **limit**: 返回数量限制 (默认 50)
    - **offset**: 偏移量 (默认 0)
    """
    # 权限验证
    if user_id != current_user_id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户的计划"
        )
    
    return BettingPlanService.get_user_plans(db, user_id, status, limit, offset)


@router.get("/users/{user_id}/statistics")
def get_user_statistics(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的计划统计信息
    
    - **user_id**: 用户 ID
    
    返回：
    - active_plans_count: 进行中的计划数量
    - pending_plans_count: 待接受的计划数量
    - waiting_double_check_count: 待二次确认的计划数量
    - completed_plans_count: 已完成的计划数量
    - total_check_in_days: 累计打卡天数
    """
    # 权限验证
    if user_id != current_user_id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户的统计信息"
        )
    
    from app.models.check_in import CheckIn
    from sqlalchemy import func
    
    # 统计各状态的计划数量
    active_count = db.query(BettingPlan).filter(
        ((BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)),
        BettingPlan.status == PlanStatus.ACTIVE
    ).count()
    
    # 统计待处理计划：包括自己创建的pending计划和被邀请的所有未处理计划
    from app.models.invitation import Invitation, InvitationStatus
    invited_pending_count = db.query(Invitation).filter(
        Invitation.invitee_id == user_id,
        Invitation.status.in_([InvitationStatus.PENDING, InvitationStatus.VIEWED])
    ).count()
    
    own_pending_count = db.query(BettingPlan).filter(
        ((BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)),
        BettingPlan.status == PlanStatus.PENDING
    ).count()
    
    pending_count = own_pending_count + invited_pending_count
    
    waiting_double_check_count = db.query(BettingPlan).filter(
        ((BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)),
        BettingPlan.status == PlanStatus.WAITING_DOUBLE_CHECK
    ).count()
    
    completed_count = db.query(BettingPlan).filter(
        ((BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)),
        BettingPlan.status == PlanStatus.COMPLETED
    ).count()
    
    # 统计打卡天数（去重）
    total_check_in_days = db.query(func.count(func.distinct(CheckIn.check_in_date))).filter(
        CheckIn.user_id == user_id
    ).scalar() or 0
    
    return {
        "active_plans_count": active_count,
        "pending_plans_count": pending_count,
        "waiting_double_check_count": waiting_double_check_count,
        "completed_plans_count": completed_count,
        "total_check_in_days": total_check_in_days
    }


class DoubleCheckRequest(BaseModel):
    action: str  # "confirm" 或 "cancel"
    comment: Optional[str] = None


@router.post("/{plan_id}/doublecheck", response_model=PlanResponse)
def doublecheck_plan(
    plan_id: str,
    request: DoubleCheckRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    双重确认接口（创建者在被邀请方接受后确认或撤销）
    - action: "confirm" | "cancel"
    """
    action = request.action.lower()
    if action == "confirm":
        return BettingPlanService.confirm_plan(db, plan_id, current_user_id)
    elif action in ["cancel", "reject"]:
        # 使用 reject_plan 做撤销/拒绝处理
        return BettingPlanService.reject_plan(db, plan_id, current_user_id)
    else:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="未知的 action 值")
