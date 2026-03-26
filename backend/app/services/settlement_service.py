"""  
结算服务
基于用户选择进行结算（不再自动根据打卡数据判定）
"""
import uuid
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
from app.logger import get_logger

logger = get_logger()


class SettlementService:
    """结算服务类"""
    
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
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
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
        
        # 应用结算规则
        total_bet = plan.bet_amount * 2
        
        if creator_achieved and participant_achieved:
            # 双方都达成: 原路返还,无手续费
            creator_amount = plan.bet_amount
            participant_amount = plan.bet_amount
            platform_fee = 0.0
            logger.info("Both achieved goals for plan {}", plan_id)
        elif not creator_achieved and not participant_achieved:
            # 双方都未达成: 扣除 10% 手续费后返还
            platform_fee = total_bet * 0.10
            remaining = total_bet - platform_fee
            creator_amount = remaining / 2
            participant_amount = remaining / 2
            logger.info("Neither achieved goals for plan {}, platform fee: {}", plan_id, platform_fee)
        elif creator_achieved and not participant_achieved:
            # 创建者达成,参与者未达成: 创建者获得全部
            creator_amount = total_bet
            participant_amount = 0.0
            platform_fee = 0.0
            logger.info("Creator achieved goal for plan {}", plan_id)
        else:
            # 参与者达成,创建者未达成: 参与者获得全部
            creator_amount = 0.0
            participant_amount = total_bet
            platform_fee = 0.0
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
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
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
            
        # 根据匹配结果确定输赢和金额分配
        total_bet = plan.bet_amount * 2
            
        if matching_result.get("both_achieved"):
            # 双方都达成：原路返还，无手续费
            creator_amount = plan.bet_amount
            participant_amount = plan.bet_amount
            platform_fee = 0.0
            creator_achieved = True
            participant_achieved = True
            logger.info("Both achieved goals for plan {}", plan_id)
                
        elif matching_result.get("both_failed"):
            # 双方都未达成：扣除 10% 手续费后返还
            platform_fee = total_bet * 0.10
            remaining = total_bet - platform_fee
            creator_amount = remaining / 2
            participant_amount = remaining / 2
            creator_achieved = False
            participant_achieved = False
            logger.info("Neither achieved goals for plan {}, platform fee: {}", plan_id, platform_fee)
                
        elif matching_result.get("creator_won") is True:
            # 创建者获胜：创建者获得全部
            creator_amount = total_bet
            participant_amount = 0.0
            platform_fee = 0.0
            creator_achieved = True
            participant_achieved = False
            logger.info("Creator won for plan {}", plan_id)
                
        elif matching_result.get("creator_won") is False:
            # 参与者获胜：参与者获得全部
            creator_amount = 0.0
            participant_amount = total_bet
            platform_fee = 0.0
            creator_achieved = False
            participant_achieved = True
            logger.info("Participant won for plan {}", plan_id)
                
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的匹配结果"
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
                    
            # 1. 解冻双方资金
            creator_unfreeze_success = PaymentService.unfreeze_funds(db, plan.creator_id, plan_id)
            if not creator_unfreeze_success:
                raise Exception("Failed to unfreeze funds for creator {}", plan.creator_id)
                    
            participant_unfreeze_success = PaymentService.unfreeze_funds(db, plan.participant_id, plan_id)
            if not participant_unfreeze_success:
                raise Exception("Failed to unfreeze funds for participant {}", plan.participant_id)
                    
            # 2. 转账给创建者 (如果有金额)
            if creator_amount > 0:
                # 注意：这里假设有一个平台账户，实际实现中需要处理
                # 暂时跳过实际转账，只记录日志
                logger.info("Transferring {} to creator {}", creator_amount, plan.creator_id)
                # TODO: 实现实际的转账逻辑
                    
            # 3. 转账给参与者 (如果有金额)
            if participant_amount > 0:
                logger.info("Transferring {} to participant {}", participant_amount, plan.participant_id)
                # TODO: 实现实际的转账逻辑
                    
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
                    
            # TODO: 发送结算通知给双方
                    
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
