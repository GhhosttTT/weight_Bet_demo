"""
结算选择服务
处理用户提交结算选择、比对双方选择、执行匹配逻辑
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.models.settlement_choice import SettlementChoice
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.settlement import Settlement
from app.models.dispute import Dispute
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
    def _choices_are_matched(creator_choice: SettlementChoice, participant_choice: SettlementChoice) -> bool:
        """只读取当前轮次的选择，判断是否已经形成可结算的共识。"""
        return (
            (creator_choice.self_achieved and creator_choice.opponent_achieved and
             participant_choice.self_achieved and participant_choice.opponent_achieved)
            or
            (not creator_choice.self_achieved and not creator_choice.opponent_achieved and
             not participant_choice.self_achieved and not participant_choice.opponent_achieved)
            or
            (creator_choice.self_achieved and not creator_choice.opponent_achieved and
             not participant_choice.self_achieved and participant_choice.opponent_achieved)
            or
            (not creator_choice.self_achieved and creator_choice.opponent_achieved and
             participant_choice.self_achieved and not participant_choice.opponent_achieved)
        )

    @staticmethod
    def _validate_settlement_window(plan: BettingPlan) -> None:
        """确保计划已经进入可结算窗口。"""
        if plan.status != PlanStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有进行中的计划可以提交结算选择"
            )
        if not plan.participant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划尚未形成完整参与关系，无法提交结算选择"
            )

        current_time = (
            datetime.now(plan.end_date.tzinfo)
            if plan.end_date.tzinfo else datetime.utcnow()
        )
        if current_time < plan.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划尚未到期，暂不能提交结算选择"
            )
    
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
        plan = db.query(BettingPlan).filter(
            BettingPlan.id == plan_id
        ).with_for_update().first()
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
        
        # 已存在结算记录时，计划状态可能尚未被旧数据同步，仍需禁止追加选择。
        if (
            plan.status == PlanStatus.COMPLETED
            or db.query(Settlement).filter(Settlement.plan_id == plan_id).first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划已结算"
            )

        SettlementChoiceService._validate_settlement_window(plan)
        
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
            
            return SettlementChoiceResponse.model_validate(choice)
            
        except Exception as e:
            db.rollback()
            if isinstance(e, IntegrityError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="您已在当前轮次提交过选择"
                )
            logger.error("Failed to submit settlement choice: {}", str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="提交选择失败，请稍后重试"
            )
    
    @staticmethod
    def _get_current_round(db: Session, plan_id: str) -> int:
        """读取计划持久化的当前轮次。"""
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            return 1
        return plan.settlement_round or 1
    
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

        if user_id not in (plan.creator_id, plan.participant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该计划的参与者"
            )

        current_round = SettlementChoiceService._get_current_round(db, plan_id)

        # 查询接口允许已完成计划读取最终状态；变更接口仍由窗口校验拦截。
        settlement = db.query(Settlement).filter(
            Settlement.plan_id == plan_id
        ).first()
        if not settlement:
            SettlementChoiceService._validate_settlement_window(plan)
        
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

        current_user_choice = (
            creator_choice if user_id == plan.creator_id else participant_choice
        )
        current_user_dispute = None
        if settlement:
            current_user_dispute = db.query(Dispute).filter(
                Dispute.settlement_id == settlement.id,
                Dispute.user_id == user_id,
            ).first()
        choices_matched = bool(
            creator_choice and participant_choice and
            SettlementChoiceService._choices_are_matched(creator_choice, participant_choice)
        )
        
        # 检查是否已结算
        return SettlementSelectionStatus(
            plan_id=plan_id,
            current_round=current_round,
            creator_submitted=creator_choice is not None,
            participant_submitted=participant_choice is not None,
            current_user_submitted=current_user_choice is not None,
            creator_choice=SettlementChoiceResponse.model_validate(creator_choice) if creator_choice else None,
            participant_choice=SettlementChoiceResponse.model_validate(participant_choice) if participant_choice else None,
            matched=choices_matched,
            settlement_completed=settlement is not None,
            in_arbitration=bool(settlement and settlement.in_arbitration),
            settlement_id=settlement.id if settlement else None,
            dispute_status=current_user_dispute.status if current_user_dispute else None,
            dispute_admin_notes=current_user_dispute.admin_notes if current_user_dispute else None,
        )
    
    @staticmethod
    def match_choices(
        db: Session,
        plan_id: str,
        requesting_user_id: Optional[str] = None
    ) -> SettlementMatchingResult:
        """
        比对双方选择并执行匹配逻辑
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            
        Returns:
            SettlementMatchingResult: 匹配结果
        """
        # 匹配和推进轮次共享同一计划行锁，避免两个匹配请求同时
        # 读取旧轮次并重复推进。
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).with_for_update().first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )

        if requesting_user_id and requesting_user_id not in (plan.creator_id, plan.participant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该计划的参与者"
            )

        existing_settlement = db.query(Settlement).filter(
            Settlement.plan_id == plan_id
        ).first()
        if existing_settlement:
            if existing_settlement.in_arbitration:
                return SettlementMatchingResult(
                    matched=False,
                    go_to_arbitration=True,
                    message="计划已进入仲裁流程",
                )
            both_achieved = bool(
                existing_settlement.creator_achieved and
                existing_settlement.participant_achieved
            )
            both_failed = bool(
                not existing_settlement.creator_achieved and
                not existing_settlement.participant_achieved
            )
            creator_won = (
                True if existing_settlement.creator_achieved and not existing_settlement.participant_achieved
                else False if not existing_settlement.creator_achieved and existing_settlement.participant_achieved
                else None
            )
            return SettlementMatchingResult(
                matched=True,
                creator_won=creator_won,
                both_achieved=both_achieved,
                both_failed=both_failed,
                message="计划已完成结算",
            )

        SettlementChoiceService._validate_settlement_window(plan)
        
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
            # 新流程会在第二位用户提交后自动推进轮次；兼容旧客户端随后
            # 立即调用 /match 的行为，返回上一轮已经发生的不匹配结果。
            if not creator_choice and not participant_choice and current_round > 1:
                previous_creator_choice = db.query(SettlementChoice).filter(
                    SettlementChoice.plan_id == plan_id,
                    SettlementChoice.user_id == plan.creator_id,
                    SettlementChoice.round == current_round - 1
                ).first()
                previous_participant_choice = db.query(SettlementChoice).filter(
                    SettlementChoice.plan_id == plan_id,
                    SettlementChoice.user_id == plan.participant_id,
                    SettlementChoice.round == current_round - 1
                ).first()
                if (
                    previous_creator_choice and previous_participant_choice and
                    not SettlementChoiceService._choices_are_matched(
                        previous_creator_choice, previous_participant_choice
                    )
                ):
                    return SettlementMatchingResult(
                        matched=False,
                        go_to_next_round=True,
                        message="上一轮选择不匹配，已进入下一轮",
                    )
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
            # 选择不匹配后立即持久化轮次，下一次提交才能进入下一轮。
            plan.settlement_round = current_round + 1
            db.commit()
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
        timeout_hours: int = 24,
        requesting_user_id: Optional[str] = None
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
        # 超时推进也会修改 settlement_round 或启动仲裁，必须与匹配入口
        # 使用同一把计划行锁。
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).with_for_update().first()
        if not plan:
            return False, "计划不存在"

        if requesting_user_id and requesting_user_id not in (plan.creator_id, plan.participant_id):
            return False, "您不是该计划的参与者"

        if db.query(Settlement).filter(Settlement.plan_id == plan_id).first():
            return False, "计划已结算"

        if plan.status != PlanStatus.ACTIVE:
            return False, "只有进行中的计划可以检查结算超时"
        if not plan.participant_id:
            return False, "计划尚未形成完整参与关系"
        current_time = (
            datetime.now(plan.end_date.tzinfo)
            if plan.end_date.tzinfo else datetime.utcnow()
        )
        if current_time < plan.end_date:
            return False, "计划尚未到期"

        if timeout_hours < 1 or timeout_hours > 168:
            return False, "超时时间必须在 1 到 168 小时之间"
        
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
            plan.settlement_round = next_round
            db.commit()
            return True, f"Timeout, entered round {next_round}"
