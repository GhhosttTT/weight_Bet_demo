"""
结算选择服务
处理用户提交结算选择、比对双方选择、执行匹配逻辑
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.models.settlement_choice import SettlementChoice
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.settlement import Settlement
from app.schemas.settlement_choice import (
    SettlementChoiceRequest,
    SettlementChoiceResponse,
    SettlementSelectionStatus,
    SettlementMatchingResult
)
from app.services.arbitration_service import ArbitrationService
from app.logger import get_logger

logger = get_logger()


class SettlementChoiceService:
    """结算选择服务类"""
    
    @staticmethod
    def submit_choice(
        db: Session,
        plan_id: str,
        user_id: str,
        request: SettlementChoiceRequest
    ) -> SettlementChoiceResponse:
        """
        提交结算选择
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            request: 选择请求
            
        Returns:
            SettlementChoiceResponse: 选择响应
            
        Raises:
            HTTPException: 计划不存在、已结算或重复提交
        """
        # 获取计划
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )
        
        # 验证用户是参与者
        if user_id != plan.creator_id and user_id != plan.participant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该计划的参与者"
            )
        
        # 检查计划状态
        if plan.status == PlanStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划已结算"
            )
        
        # 确定当前轮次
        current_round = SettlementChoiceService._get_current_round(db, plan_id)
        if current_round > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已超过最大选择轮次"
            )
        
        # 检查用户是否已在当前轮次提交
        existing_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == user_id,
            SettlementChoice.round == current_round
        ).first()
        
        if existing_choice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"您已在第{current_round}轮提交过选择"
            )
        
        # 创建选择记录
        choice_id = str(uuid.uuid4())
        choice = SettlementChoice(
            id=choice_id,
            plan_id=plan_id,
            user_id=user_id,
            self_achieved=request.self_achieved,
            opponent_achieved=request.opponent_achieved,
            round=current_round
        )
        
        try:
            db.add(choice)
            db.commit()
            db.refresh(choice)
            
            logger.info(
                "User submitted settlement choice: user={}, plan={}, round={}, self={}, opponent={}",
                user_id, plan_id, current_round, request.self_achieved, request.opponent_achieved
            )
            
            return SettlementChoiceResponse.from_orm(choice)
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to submit settlement choice: {}", str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="提交选择失败：{}".format(str(e))
            )
    
    @staticmethod
    def _get_current_round(db: Session, plan_id: str) -> int:
        """获取当前轮次（不自动推进，需要显式调用 advance_round）"""
        latest_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id
        ).order_by(SettlementChoice.round.desc()).first()
        
        if not latest_choice:
            return 1
        
        # 返回最新的轮次，不自动推进
        return latest_choice.round
    
    @staticmethod
    def get_selection_status(
        db: Session,
        plan_id: str,
        user_id: str
    ) -> SettlementSelectionStatus:
        """
        获取结算选择状态
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            
        Returns:
            SettlementSelectionStatus: 选择状态
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )
        
        current_round = SettlementChoiceService._get_current_round(db, plan_id)
        
        # 获取双方选择
        creator_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == plan.creator_id,
            SettlementChoice.round == current_round
        ).first()
        
        participant_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == plan.participant_id,
            SettlementChoice.round == current_round
        ).first()
        
        # 检查是否已结算
        settlement_exists = db.query(Settlement).filter(
            Settlement.plan_id == plan_id
        ).first() is not None
        
        return SettlementSelectionStatus(
            plan_id=plan_id,
            current_round=current_round,
            creator_submitted=creator_choice is not None,
            participant_submitted=participant_choice is not None,
            creator_choice=SettlementChoiceResponse.from_orm(creator_choice) if creator_choice else None,
            participant_choice=SettlementChoiceResponse.from_orm(participant_choice) if participant_choice else None,
            matched=False,  # 将在比对接口中设置
            settlement_completed=settlement_exists,
            in_arbitration=current_round > 3
        )
    
    @staticmethod
    def match_choices(
        db: Session,
        plan_id: str
    ) -> SettlementMatchingResult:
        """
        比对双方选择并执行匹配逻辑
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            
        Returns:
            SettlementMatchingResult: 匹配结果
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )
        
        current_round = SettlementChoiceService._get_current_round(db, plan_id)
        
        # 获取双方选择
        creator_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == plan.creator_id,
            SettlementChoice.round == current_round
        ).first()
        
        participant_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == plan.participant_id,
            SettlementChoice.round == current_round
        ).first()
        
        # 检查双方是否都已提交
        if not creator_choice or not participant_choice:
            return SettlementMatchingResult(
                matched=False,
                go_to_next_round=False,
                go_to_arbitration=False,
                message="等待双方提交选择"
            )
        
        logger.info(
            "Matching choices for plan {} round {}: Creator(self={}, opp={}), Participant(self={}, opp={})",
            plan_id, current_round,
            creator_choice.self_achieved, creator_choice.opponent_achieved,
            participant_choice.self_achieved, participant_choice.opponent_achieved
        )
        
        # 匹配逻辑
        # 情况 1: 双方都选"都达成"
        if (creator_choice.self_achieved and creator_choice.opponent_achieved and
            participant_choice.self_achieved and participant_choice.opponent_achieved):
            logger.info("Both chose 'both achieved' for plan {}", plan_id)
            return SettlementMatchingResult(
                matched=True,
                both_achieved=True,
                creator_won=None,
                go_to_next_round=False,
                go_to_arbitration=False,
                message="双方都达成目标，保证金原路返还"
            )
        
        # 情况 2: 双方都选"都未达成"
        if (not creator_choice.self_achieved and not creator_choice.opponent_achieved and
            not participant_choice.self_achieved and not participant_choice.opponent_achieved):
            logger.info("Both chose 'both failed' for plan {}", plan_id)
            return SettlementMatchingResult(
                matched=True,
                both_achieved=False,
                both_failed=True,
                creator_won=None,
                go_to_next_round=False,
                go_to_arbitration=False,
                message="双方都未达成目标，扣除 10% 平台费后平分"
            )
        
        # 情况 3: 一方选"我成对方败"，另一方选"我败对方成"（匹配成功）
        if (creator_choice.self_achieved and not creator_choice.opponent_achieved and
            not participant_choice.self_achieved and participant_choice.opponent_achieved):
            logger.info("Choices matched: Creator won for plan {}", plan_id)
            return SettlementMatchingResult(
                matched=True,
                creator_won=True,
                go_to_next_round=False,
                go_to_arbitration=False,
                message="选择匹配，创建者获胜"
            )
        
        if (not creator_choice.self_achieved and creator_choice.opponent_achieved and
            participant_choice.self_achieved and not participant_choice.opponent_achieved):
            logger.info("Choices matched: Participant won for plan {}", plan_id)
            return SettlementMatchingResult(
                matched=True,
                creator_won=False,
                go_to_next_round=False,
                go_to_arbitration=False,
                message="选择匹配，参与者获胜"
            )
        
        # 情况 4: 选择不匹配
        logger.info("Choices did not match for plan {} round {}", plan_id, current_round)
        
        if current_round >= 3:
            logger.info("Three rounds failed, going to arbitration for plan {}", plan_id)
            return SettlementMatchingResult(
                matched=False,
                go_to_next_round=False,
                go_to_arbitration=True,
                message="三次选择不匹配，进入强制仲裁"
            )
        else:
            logger.info("Going to next round for plan {}", plan_id)
            return SettlementMatchingResult(
                matched=False,
                go_to_next_round=True,
                go_to_arbitration=False,
                message="选择不匹配，进入下一轮"
            )
    
    @staticmethod
    def check_timeout_and_advance(
        db: Session,
        plan_id: str,
        timeout_hours: int = 24
    ) -> Tuple[bool, str]:
        """
        检查超时并自动推进（如果一方超时未选）
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            timeout_hours: 超时小时数（默认 24 小时）
            
        Returns:
            Tuple[bool, str]: (是否成功推进，消息)
        """
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            return False, "计划不存在"
        
        current_round = SettlementChoiceService._get_current_round(db, plan_id)
        
        # 如果已经超过 3 轮，不需要处理
        if current_round > 3:
            return False, "已在仲裁流程中"
        
        # 获取双方选择
        creator_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == plan.creator_id,
            SettlementChoice.round == current_round
        ).first()
        
        participant_choice = db.query(SettlementChoice).filter(
            SettlementChoice.plan_id == plan_id,
            SettlementChoice.user_id == plan.participant_id,
            SettlementChoice.round == current_round
        ).first()
        
        # 如果双方都已提交，不需要处理
        if creator_choice and participant_choice:
            return False, f"第{current_round}轮双方均已提交"
        
        # 检查先提交的一方是否超时等待
        first_choice = creator_choice or participant_choice
        if not first_choice:
            return False, f"第{current_round}轮尚未开始"
        
        # 检查是否超时
        time_since_submission = datetime.utcnow() - first_choice.created_at
        if time_since_submission < timedelta(hours=timeout_hours):
            remaining_hours = timeout_hours - time_since_submission.total_seconds() / 3600
            return False, f"等待对方提交，剩余{remaining_hours:.1f}小时"
        
        # 已超时，标记当日无效，进入下一轮
        logger.info(
            "User timed out for plan {} round {}: user={}, waiting_user={}",
            plan_id, current_round,
            first_choice.user_id,
            plan.participant_id if creator_choice else plan.creator_id
        )
        
        # 进入下一轮
        next_round = current_round + 1
        
        if next_round > 3:
            # 直接进入仲裁
            logger.info("Timeout exceeded 3 rounds, going to arbitration for plan {}", plan_id)
            try:
                ArbitrationService.start_arbitration(db, plan_id)
                return True, "对方超时，进入仲裁流程"
            except Exception as e:
                logger.error("Failed to start arbitration on timeout: {}", str(e))
                return False, "进入仲裁失败"
        else:
            logger.info("Timeout, advancing to round {} for plan {}", next_round, plan_id)
            return True, f"Timeout, entered round {next_round}"
