"""
结算相关的 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.betting_plan import BettingPlan
from app.models.settlement import Settlement
from app.models.dispute import Dispute, DisputeStatus
from app.services.settlement_service import SettlementService
from app.schemas.settlement import SettlementResponse, SettlementCalculation
from app.schemas.dispute import DisputeCreate, DisputeResponse
from app.logger import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/settlements/execute/{plan_id}", response_model=SettlementResponse)
async def execute_settlement(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    执行结算
    
    Args:
        plan_id: 计划 ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SettlementResponse: 结算响应
    """
    # 验证用户是计划参与者
    plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    if plan.creator_id != current_user.id and plan.participant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该计划的参与者"
        )
    
    return SettlementService.execute_settlement(db, plan_id)


@router.get("/settlements/{settlement_id}", response_model=SettlementResponse)
async def get_settlement_details(
    settlement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取结算详情
    
    Args:
        settlement_id: 结算 ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SettlementResponse: 结算响应
    """
    settlement = SettlementService.get_settlement_details(db, settlement_id)
    
    # 验证用户权限
    plan = db.query(BettingPlan).filter(BettingPlan.id == settlement.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联计划不存在"
        )
    
    if plan.creator_id != current_user.id and plan.participant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权查看此结算记录"
        )
    
    return settlement


@router.get("/settlements/plan/{plan_id}", response_model=Optional[SettlementResponse])
async def get_settlement_by_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据计划 ID 获取结算记录
    
    Args:
        plan_id: 计划 ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        Optional[SettlementResponse]: 结算响应
    """
    # 验证用户权限
    plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    if plan.creator_id != current_user.id and plan.participant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该计划的参与者"
        )
    
    return SettlementService.get_settlement_by_plan(db, plan_id)


@router.get("/settlements/calculate/{plan_id}", response_model=SettlementCalculation)
async def calculate_settlement(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    计算结算结果(预览)
    
    Args:
        plan_id: 计划 ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SettlementCalculation: 结算计算结果
    """
    # 验证用户权限
    plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    if plan.creator_id != current_user.id and plan.participant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该计划的参与者"
        )
    
    return SettlementService.calculate_settlement(db, plan_id)


@router.post("/settlements/{settlement_id}/dispute", response_model=DisputeResponse)
async def submit_dispute(
    settlement_id: str,
    dispute_data: DisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交结算争议
    
    Args:
        settlement_id: 结算 ID
        dispute_data: 争议数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        DisputeResponse: 争议响应
    """
    # 验证结算记录存在
    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="结算记录不存在"
        )
    
    # 验证用户是计划参与者
    plan = db.query(BettingPlan).filter(BettingPlan.id == settlement.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联计划不存在"
        )
    
    if plan.creator_id != current_user.id and plan.participant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该计划的参与者"
        )
    
    # 检查是否已经提交过争议
    existing_dispute = db.query(Dispute).filter(
        Dispute.settlement_id == settlement_id,
        Dispute.user_id == current_user.id
    ).first()
    
    if existing_dispute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经提交过争议"
        )
    
    try:
        # 创建争议记录
        dispute_id = str(uuid.uuid4())
        dispute = Dispute(
            id=dispute_id,
            settlement_id=settlement_id,
            user_id=current_user.id,
            reason=dispute_data.reason,
            description=dispute_data.description,
            status=DisputeStatus.PENDING
        )
        
        db.add(dispute)
        db.commit()
        db.refresh(dispute)
        
        logger.info(
            f"Dispute submitted: id={dispute_id}, settlement={settlement_id}, user={current_user.id}",
            extra={
                "dispute_id": dispute_id,
                "settlement_id": settlement_id,
                "user_id": current_user.id
            }
        )
        
        # TODO: 发送通知给管理员
        logger.info("Notifying administrators about dispute {}", dispute_id)
        
        return DisputeResponse.from_orm(dispute)
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to submit dispute: {}", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="提交争议失败: {}".format(str(e))
        )


@router.post("/settlements/scheduled-task")
async def run_scheduled_settlement_task(
    db: Session = Depends(get_db),
    limit: int = 100
):
    """
    运行定时结算任务
    
    注意: 此接口应该由定时任务调度器调用,需要添加适当的认证机制
    
    Args:
        db: 数据库会话
        limit: 处理数量限制
        
    Returns:
        dict: 处理结果统计
    """
    # TODO: 添加 API 密钥或其他认证机制
    return SettlementService.process_scheduled_settlements(db, limit)
