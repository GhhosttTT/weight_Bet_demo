"""
仲裁服务
处理三次选择不匹配后的强制仲裁流程
"""
import uuid
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.models.settlement import Settlement
from app.models.betting_plan import BettingPlan, PlanStatus
from app.schemas.settlement import SettlementResponse
from app.services.payment_service import PaymentService
from app.logger import get_logger

logger = get_logger()


class ArbitrationService:
    """仲裁服务类"""

    _CENT = Decimal("0.01")
    
    @staticmethod
    def start_arbitration(
        db: Session,
        plan_id: str
    ) -> SettlementResponse:
        """
        开始仲裁流程（扣除 15% 仲裁费，根据实际打卡数据判定）
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            
        Returns:
            SettlementResponse: 结算响应
            
        Raises:
            HTTPException: 计划不存在或不符合仲裁条件
        """
        from app.services.check_in_service import CheckInService
        
        # 获取计划
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).with_for_update().first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )

        if plan.status != PlanStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有进行中的计划可以仲裁"
            )
        if not plan.participant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划尚未形成完整参与关系，无法仲裁"
            )
        current_time = datetime.now(plan.end_date.tzinfo) if plan.end_date.tzinfo else datetime.utcnow()
        if current_time < plan.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划尚未到期"
            )
        
        # 检查是否已结算
        existing_settlement = db.query(Settlement).filter(
            Settlement.plan_id == plan_id
        ).first()
        if existing_settlement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划已结算"
            )
        
        logger.info("Starting arbitration for plan {}", plan_id)
        
        # 获取双方最终体重（基于打卡数据）
        creator_final_weight = CheckInService.get_latest_weight(
            db, plan.creator_id, plan_id
        )
        participant_final_weight = CheckInService.get_latest_weight(
            db, plan.participant_id, plan_id
        )
        
        # 如果没有打卡记录，使用初始体重
        if creator_final_weight is None:
            creator_final_weight = plan.creator_initial_weight
            logger.warning("No check-in data for creator {}, using initial weight", plan.creator_id)
        
        if participant_final_weight is None:
            participant_final_weight = plan.participant_initial_weight
            logger.warning("No check-in data for participant {}, using initial weight", plan.participant_id)
        
        # 计算实际减重量
        creator_weight_loss = plan.creator_initial_weight - creator_final_weight
        participant_weight_loss = plan.participant_initial_weight - participant_final_weight
        
        # 判断是否达成目标
        creator_achieved = creator_weight_loss >= plan.creator_target_weight_loss
        participant_achieved = participant_weight_loss >= plan.participant_target_weight_loss
        
        # 计算总金额和仲裁费
        bet_amount = Decimal(str(plan.bet_amount)).quantize(ArbitrationService._CENT, rounding=ROUND_HALF_UP)
        total_bet = (bet_amount * Decimal("2")).quantize(ArbitrationService._CENT, rounding=ROUND_HALF_UP)
        arbitration_fee = (total_bet * Decimal("0.15")).quantize(
            ArbitrationService._CENT, rounding=ROUND_HALF_UP
        )
        remaining_amount = total_bet - arbitration_fee
        
        # 根据实际达成情况分配金额
        if creator_achieved and not participant_achieved:
            # 创建者达成，参与者未达成：创建者获得剩余全部
            creator_amount = remaining_amount
            participant_amount = 0.0
            logger.info(
                "Arbitration result: Creator achieved, participant failed. Creator gets {} (fee: {})",
                creator_amount, arbitration_fee
            )
        elif participant_achieved and not creator_achieved:
            # 参与者达成，创建者未达成：参与者获得剩余全部
            creator_amount = 0.0
            participant_amount = remaining_amount
            logger.info(
                "Arbitration result: Participant achieved, creator failed. Participant gets {} (fee: {})",
                participant_amount, arbitration_fee
            )
        else:
            # 其他情况（都达成或都未达成）：平分剩余金额
            creator_amount = (remaining_amount / Decimal("2")).quantize(
                ArbitrationService._CENT, rounding=ROUND_DOWN
            )
            participant_amount = remaining_amount - creator_amount
            logger.info(
                "Arbitration result: Both {} . Splitting remaining amount: {} each (fee: {})",
                "achieved" if creator_achieved else "failed",
                creator_amount, arbitration_fee
            )
        
        creator_amount = float(creator_amount)
        participant_amount = float(participant_amount)
        arbitration_fee = float(arbitration_fee)

        # 创建结算记录
        settlement_id = str(uuid.uuid4())
        settlement = Settlement(
            id=settlement_id,
            plan_id=plan_id,
            creator_achieved=creator_achieved,
            participant_achieved=participant_achieved,
            creator_final_weight=creator_final_weight,
            participant_final_weight=participant_final_weight,
            creator_weight_loss=creator_weight_loss,
            participant_weight_loss=participant_weight_loss,
            creator_amount=creator_amount,
            participant_amount=participant_amount,
            platform_fee=arbitration_fee,
            notes="仲裁结算：三次选择不匹配后强制仲裁",
            in_arbitration=True,
            arbitration_fee=arbitration_fee
        )
        
        try:
            # 在当前事务中释放冻结本金并写入仲裁结算金额。
            if not PaymentService.release_settlement_funds(
                db, plan.creator_id, plan_id, creator_amount, settlement_id
            ):
                raise Exception("Failed to release arbitration funds for creator")
            if not PaymentService.release_settlement_funds(
                db, plan.participant_id, plan_id, participant_amount, settlement_id
            ):
                raise Exception("Failed to release arbitration funds for participant")
            
            # 4. 更新计划状态
            plan.status = PlanStatus.COMPLETED
            
            # 5. 保存结算记录
            db.add(settlement)
            
            # 6. 提交事务
            db.commit()
            db.refresh(settlement)
            
            logger.info(
                "Arbitration settlement completed: id={}, plan={}, creator_amount={}, participant_amount={}, fee={}",
                settlement_id, plan_id, creator_amount, participant_amount, arbitration_fee
            )
            
            return SettlementResponse.model_validate(settlement)
            
        except Exception as e:
            db.rollback()
            logger.error(
                "Arbitration settlement failed for plan {}: {}",
                plan_id, str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="仲裁失败，请稍后重试"
            )
