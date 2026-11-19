"""  
结算服务
基于用户选择进行结算（不再自动根据打卡数据判定）
"""
import uuid
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, date
from typing import Optional, List
from app.models.settlement import Settlement
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.settlement_choice import SettlementChoice
from app.schemas.settlement import (
    SettlementResponse,
    SettlementResult,
    SettlementCalculation
)
from app.services.check_in_service import CheckInService
from app.services.payment_service import PaymentService
from app.services.arbitration_service import ArbitrationService
from app.services.notification_service import NotificationService
from app.logger import get_logger

logger = get_logger()


class SettlementService:
    """结算服务类"""

    _CENT = Decimal("0.01")

    @classmethod
    def _calculate_payouts(cls, bet_amount, creator_achieved: bool, participant_achieved: bool):
        """按分计算结算金额，避免浮点误差和分账后资金不守恒。"""
        bet = Decimal(str(bet_amount)).quantize(cls._CENT, rounding=ROUND_HALF_UP)
        total_bet = (bet * Decimal("2")).quantize(cls._CENT, rounding=ROUND_HALF_UP)

        if creator_achieved and participant_achieved:
            return float(bet), float(bet), 0.0, float(total_bet)
        if creator_achieved and not participant_achieved:
            return float(total_bet), 0.0, 0.0, float(total_bet)
        if not creator_achieved and participant_achieved:
            return 0.0, float(total_bet), 0.0, float(total_bet)

        platform_fee = (total_bet * Decimal("0.10")).quantize(
            cls._CENT, rounding=ROUND_HALF_UP
        )
        remaining = total_bet - platform_fee
        creator_amount = (remaining / Decimal("2")).quantize(
            cls._CENT, rounding=ROUND_DOWN
        )
        participant_amount = remaining - creator_amount
        return (
            float(creator_amount),
            float(participant_amount),
            float(platform_fee),
            float(total_bet),
        )
    
    @staticmethod
    def calculate_settlement(
        db: Session,
        plan_id: str
    ) -> SettlementCalculation:
        """
        计算结算结果
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            
        Returns:
            SettlementCalculation: 结算计算结果
            
        Raises:
            HTTPException: 计划不存在或状态错误
        """
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
                detail="计划状态不允许结算"
            )
        
        # 验证计划已到期
        if datetime.now(plan.end_date.tzinfo) < plan.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划尚未到期"
            )
        
        # 获取双方最终体重
        creator_final_weight = CheckInService.get_latest_weight(
            db, plan.creator_id, plan_id
        )
        participant_final_weight = CheckInService.get_latest_weight(
            db, plan.participant_id, plan_id
        )
        
        # 如果没有打卡记录,使用初始体重(视为未达成目标)
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
        
        # 应用结算规则，所有出账金额统一保留两位小数。
        creator_amount, participant_amount, platform_fee, total_bet = SettlementService._calculate_payouts(
            plan.bet_amount, creator_achieved, participant_achieved
        )

        if creator_achieved and participant_achieved:
            # 双方都达成: 原路返还,无手续费
            logger.info("Both achieved goals for plan {}", plan_id)
        elif not creator_achieved and not participant_achieved:
            # 双方都未达成: 扣除 10% 手续费后返还
            logger.info("Neither achieved goals for plan {}, platform fee: {}", plan_id, platform_fee)
        elif creator_achieved and not participant_achieved:
            # 创建者达成,参与者未达成: 创建者获得全部
            logger.info("Creator achieved goal for plan {}", plan_id)
        else:
            # 参与者达成,创建者未达成: 参与者获得全部
            logger.info("Participant achieved goal for plan {}", plan_id)
        
        return SettlementCalculation(
            creator_amount=creator_amount,
            participant_amount=participant_amount,
            platform_fee=platform_fee,
            total_bet=total_bet
        )
    
    @staticmethod
    def execute_settlement(
        db: Session,
        plan_id: str,
        matching_result: dict = None
    ) -> SettlementResponse:
        """
        执行结算（基于用户选择匹配结果，使用数据库事务确保原子性）
            
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            matching_result: 匹配结果字典（包含 matched, creator_won, both_achieved, both_failed, go_to_arbitration）
                
        Returns:
            SettlementResponse: 结算响应
                
        Raises:
            HTTPException: 计划不存在、状态错误或已结算
        """
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
                detail="只有进行中的计划可以结算"
            )

        if not plan.participant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划尚未形成完整参与关系，无法结算"
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
            
        # 如果没有提供匹配结果，从数据库获取双方选择并比对
        if not matching_result:
            from app.services.settlement_choice_service import SettlementChoiceService
            matching_result_obj = SettlementChoiceService.match_choices(db, plan_id)
            matching_result = {
                "matched": matching_result_obj.matched,
                "creator_won": matching_result_obj.creator_won,
                "both_achieved": matching_result_obj.both_achieved,
                "both_failed": matching_result_obj.both_failed,
                "go_to_arbitration": matching_result_obj.go_to_arbitration
            }
            
        # 如果需要仲裁，调用仲裁服务
        if matching_result.get("go_to_arbitration"):
            logger.info("Going to arbitration for plan {}", plan_id)
            return ArbitrationService.start_arbitration(db, plan_id)
            
        # 验证匹配结果
        if not matching_result.get("matched"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="双方选择不匹配，无法结算"
            )
            
        # 获取双方最终体重（用于记录）
        creator_final_weight = CheckInService.get_latest_weight(
            db, plan.creator_id, plan_id
        )
        participant_final_weight = CheckInService.get_latest_weight(
            db, plan.participant_id, plan_id
        )
            
        # 如果没有打卡记录，使用初始体重
        if creator_final_weight is None:
            creator_final_weight = plan.creator_initial_weight
        if participant_final_weight is None:
            participant_final_weight = plan.participant_initial_weight
            
        # 计算实际减重量
        creator_weight_loss = plan.creator_initial_weight - creator_final_weight
        participant_weight_loss = plan.participant_initial_weight - participant_final_weight
            
        # 根据匹配结果确定输赢，再统一按分计算金额。
        if matching_result.get("both_achieved"):
            # 双方都达成：原路返还，无手续费
            creator_achieved = True
            participant_achieved = True
        elif matching_result.get("both_failed"):
            # 双方都未达成：扣除 10% 手续费后返还
            creator_achieved = False
            participant_achieved = False
        elif matching_result.get("creator_won") is True:
            # 创建者获胜：创建者获得全部
            creator_achieved = True
            participant_achieved = False
        elif matching_result.get("creator_won") is False:
            # 参与者获胜：参与者获得全部
            creator_achieved = False
            participant_achieved = True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的匹配结果"
            )

        creator_amount, participant_amount, platform_fee, total_bet = SettlementService._calculate_payouts(
            plan.bet_amount, creator_achieved, participant_achieved
        )
        
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
            platform_fee=platform_fee,
            notes=None
        )
                
        # 使用数据库事务确保所有操作的原子性
        try:
            # 开始事务 (db.begin() 已经由 FastAPI 的依赖注入处理)
            logger.info("Starting settlement transaction for plan {}", plan_id)
                    
            # 1. 在同一个事务中释放冻结本金并入账结算金额。
            if not PaymentService.release_settlement_funds(
                db, plan.creator_id, plan_id, creator_amount, settlement_id
            ):
                raise Exception("Failed to release settlement funds for creator")
            if not PaymentService.release_settlement_funds(
                db, plan.participant_id, plan_id, participant_amount, settlement_id
            ):
                raise Exception("Failed to release settlement funds for participant")
                    
            # 4. 更新计划状态
            plan.status = PlanStatus.COMPLETED
                    
            # 5. 保存结算记录
            db.add(settlement)
                    
            # 6. 提交事务
            db.commit()
            db.refresh(settlement)
                    
            logger.info(
                "Settlement completed successfully: id={}, plan={}, creator_amount={}, participant_amount={}, platform_fee={}",
                settlement_id, plan_id, creator_amount, participant_amount, platform_fee
            )
                    
            # 通知失败不能回滚已完成的资金结算，避免重复结算风险。
            for user_id, amount, achieved in (
                (plan.creator_id, creator_amount, creator_achieved),
                (plan.participant_id, participant_amount, participant_achieved),
            ):
                try:
                    NotificationService.send_settlement_notification(
                        db, user_id, plan_id, amount, achieved, settlement_id=settlement_id
                    )
                except Exception:
                    logger.exception(
                        "Settlement notification failed: plan={}, user={}",
                        plan_id,
                        user_id,
                    )
                    
            return SettlementResponse.from_orm(settlement)
                    
        except Exception as e:
            # 发生任何错误时回滚所有操作
            db.rollback()
                    
            logger.error(
                "Settlement failed for plan {}, rolling back all operations: {}",
                plan_id, str(e),
                extra={
                    "plan_id": plan_id,
                    "settlement_id": settlement_id,
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
                    
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="结算失败：{}".format(str(e))
            )
    
    @staticmethod
    def get_settlement_details(
        db: Session,
        settlement_id: str
    ) -> SettlementResponse:
        """
        获取结算详情
        
        Args:
            db: 数据库会话
            settlement_id: 结算 ID
            
        Returns:
            SettlementResponse: 结算响应
            
        Raises:
            HTTPException: 结算记录不存在
        """
        settlement = db.query(Settlement).filter(
            Settlement.id == settlement_id
        ).first()
        
        if not settlement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="结算记录不存在"
            )
        
        return SettlementResponse.from_orm(settlement)
    
    @staticmethod
    def get_settlement_by_plan(
        db: Session,
        plan_id: str
    ) -> Optional[SettlementResponse]:
        """
        根据计划 ID 获取结算记录
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            
        Returns:
            Optional[SettlementResponse]: 结算响应,如果不存在则返回 None
        """
        settlement = db.query(Settlement).filter(
            Settlement.plan_id == plan_id
        ).first()
        
        if settlement:
            return SettlementResponse.from_orm(settlement)
        
        return None
    
    @staticmethod
    def scan_expired_plans(
        db: Session,
        limit: int = 100
    ) -> List[str]:
        """
        扫描已到期但未结算的计划
        
        Args:
            db: 数据库会话
            limit: 扫描数量限制
            
        Returns:
            List[str]: 需要结算的计划 ID 列表
        """
        # 查找已到期且状态为 ACTIVE 的计划
        now = datetime.utcnow()
        expired_plans = db.query(BettingPlan).filter(
            BettingPlan.status == PlanStatus.ACTIVE,
            BettingPlan.end_date <= now
        ).limit(limit).all()
        
        # 过滤掉已结算的计划
        plan_ids = []
        for plan in expired_plans:
            existing_settlement = db.query(Settlement).filter(
                Settlement.plan_id == plan.id
            ).first()
            if not existing_settlement:
                plan_ids.append(plan.id)
        
        logger.info("Found {} expired plans to settle", len(plan_ids))
        
        return plan_ids
    
    @staticmethod
    def process_scheduled_settlements(
        db: Session,
        limit: int = 100
    ) -> dict:
        """
        处理定时结算任务
        
        Args:
            db: 数据库会话
            limit: 处理数量限制
            
        Returns:
            dict: 处理结果统计
        """
        plan_ids = SettlementService.scan_expired_plans(db, limit)
        
        success_count = 0
        failed_count = 0
        failed_plans = []
        
        for plan_id in plan_ids:
            try:
                SettlementService.execute_settlement(db, plan_id)
                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_plans.append({
                    "plan_id": plan_id,
                    "error": str(e)
                })
                logger.error("Failed to settle plan {}: {}", plan_id, str(e))
        
        result = {
            "total": len(plan_ids),
            "success": success_count,
            "failed": failed_count,
            "failed_plans": failed_plans
        }
        
        logger.info("Scheduled settlement completed: {}", result)
        
        return result
