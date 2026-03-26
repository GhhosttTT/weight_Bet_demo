"""
结算选择相关的 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.betting_plan import BettingPlan
from app.models.settlement import Settlement
from app.schemas.settlement_choice import (
    SettlementChoiceRequest,
    SettlementChoiceResponse,
    SettlementSelectionStatus,
    SettlementMatchingResult,
    PlanSettlementInfo
)
from app.services.settlement_choice_service import SettlementChoiceService
from app.services.settlement_service import SettlementService
from app.logger import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/settlement-choices/{plan_id}", response_model=SettlementChoiceResponse)
async def submit_settlement_choice(
    plan_id: str,
    request: SettlementChoiceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交结算选择
    
    Args:
        plan_id: 计划 ID
        request: 选择请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SettlementChoiceResponse: 选择响应
    """
    return SettlementChoiceService.submit_choice(
        db, plan_id, current_user.id, request
    )


@router.get("/settlement-choices/{plan_id}/status", response_model=SettlementSelectionStatus)
async def get_selection_status(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取结算选择状态
    
    Args:
        plan_id: 计划 ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SettlementSelectionStatus: 选择状态
    """
    return SettlementChoiceService.get_selection_status(
        db, plan_id, current_user.id
    )


@router.post("/settlement-choices/{plan_id}/match", response_model=SettlementMatchingResult)
async def match_settlement_choices(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    比对双方结算选择
    
    注意：此接口应该由定时任务或管理员调用，需要添加适当的认证机制
    
    Args:
        plan_id: 计划 ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SettlementMatchingResult: 匹配结果
    """
    # TODO: 添加 API 密钥或其他认证机制
    result = SettlementChoiceService.match_choices(db, plan_id)
    
    logger.info(
        "Settlement matching result for plan {}: matched={}, creator_won={}, arbitration={}",
        plan_id, result.matched, result.creator_won, result.go_to_arbitration
    )
    
    return result


@router.get("/settlement-choices/{plan_id}/check-timeout")
async def check_timeout_and_advance(
    plan_id: str,
    timeout_hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    检查超时并自动推进到下一轮
    
    注意：此接口应该由定时任务调用
    
    Args:
        plan_id: 计划 ID
        timeout_hours: 超时小时数
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        dict: 处理结果
    """
    # TODO: 添加 API 密钥或其他认证机制
    success, message = SettlementChoiceService.check_timeout_and_advance(
        db, plan_id, timeout_hours
    )
    
    return {
        "success": success,
        "message": message
    }


@router.get("/settlement-check", response_model=List[PlanSettlementInfo])
async def check_settlement_deadline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    检查用户的计划是否到达结算日（用于 App 启动时弹窗提醒）
    
    Returns:
        List[PlanSettlementInfo]: 需要结算的计划列表
    """
    current_time = datetime.now()
    
    # 查询用户相关的所有 active 状态且已到期的计划
    expired_plans = db.query(BettingPlan).filter(
        BettingPlan.status == "active",
        BettingPlan.end_date <= current_time,
        ((BettingPlan.creator_id == current_user.id) | 
         (BettingPlan.participant_id == current_user.id))
    ).all()
    
    result = []
    for plan in expired_plans:
        # 检查是否已存在结算记录
        settlement = SettlementService.get_settlement_by_plan(db, plan.id)
        
        # 检查双方选择提交状态
        selection_status = None
        try:
            selection_status = SettlementChoiceService.get_selection_status(
                db, plan.id, current_user.id
            )
        except Exception:
            pass
        
        plan_info = PlanSettlementInfo(
            plan_id=plan.id,
            description=plan.description,
            end_date=plan.end_date,
            bet_amount=plan.bet_amount,
            has_settlement=settlement is not None,
            in_progress=(selection_status is not None and 
                        not selection_status.settlement_completed and
                        not selection_status.in_arbitration)
        )
        result.append(plan_info)
    
    return result
