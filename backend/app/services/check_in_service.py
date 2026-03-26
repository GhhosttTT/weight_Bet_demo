"""
打卡服务
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime, date
from typing import List, Optional
from app.models.check_in import CheckIn, ReviewStatus
from app.models.betting_plan import BettingPlan, PlanStatus
from app.schemas.check_in import (
    CreateCheckInRequest,
    ReviewCheckInRequest,
    CheckInResponse,
    ProgressStats
)
from app.logger import get_logger

logger = get_logger()


class CheckInService:
    """打卡服务类"""
    
    @staticmethod
    def create_check_in(
        db: Session,
        user_id: str,
        request: CreateCheckInRequest
    ) -> CheckInResponse:
        """
        创建打卡记录
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            request: 创建打卡请求
            
        Returns:
            CheckInResponse: 打卡记录响应
            
        Raises:
            HTTPException: 验证失败或创建失败
        """
        # 验证计划存在且用户是参与者
        plan = db.query(BettingPlan).filter(BettingPlan.id == request.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )
        
        # 验证用户是计划参与者
        if plan.creator_id != user_id and plan.participant_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该计划的参与者"
            )
        
        # 验证计划状态
        if plan.status != PlanStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划未激活,无法打卡"
            )
        
        # 验证打卡日期在计划期间内
        if request.check_in_date < plan.start_date.date() or request.check_in_date > plan.end_date.date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="打卡日期不在计划期间内"
            )
        
        # 检查是否重复打卡
        existing_check_in = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.plan_id == request.plan_id,
                CheckIn.check_in_date == request.check_in_date
            )
        ).first()
        
        if existing_check_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="今日已打卡"
            )
        
        # 验证体重变化合理性
        review_status = ReviewStatus.APPROVED
        previous_check_ins = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.plan_id == request.plan_id,
                CheckIn.check_in_date < request.check_in_date
            )
        ).order_by(CheckIn.check_in_date.desc()).limit(1).all()
        
        if previous_check_ins:
            last_check_in = previous_check_ins[0]
            weight_change = abs(request.weight - last_check_in.weight)
            days_diff = (request.check_in_date - last_check_in.check_in_date).days
            
            # 每天体重变化超过 2kg 标记为待审核
            if days_diff > 0 and weight_change / days_diff > 2.0:
                review_status = ReviewStatus.PENDING
                logger.warning(
                    f"Abnormal weight change detected: user={user_id}, "
                    f"change={weight_change}kg in {days_diff} days"
                )
        
        # 创建打卡记录
        check_in_id = str(uuid.uuid4())
        check_in = CheckIn(
            id=check_in_id,
            user_id=user_id,
            plan_id=request.plan_id,
            weight=request.weight,
            check_in_date=request.check_in_date,
            photo_url=request.photo_url,
            note=request.note,
            review_status=review_status
        )
        
        db.add(check_in)
        db.commit()
        db.refresh(check_in)
        
        logger.info(
            f"Check-in created: id={check_in_id}, user={user_id}, "
            f"plan={request.plan_id}, status={review_status}"
        )
        
        return CheckInResponse.from_orm(check_in)
    
    @staticmethod
    def upload_photo(
        db: Session,
        user_id: str,
        check_in_id: str,
        photo_url: str
    ) -> CheckInResponse:
        """
        上传体重秤照片
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            check_in_id: 打卡记录 ID
            photo_url: 照片 URL
            
        Returns:
            CheckInResponse: 更新后的打卡记录
            
        Raises:
            HTTPException: 打卡记录不存在或无权限
        """
        check_in = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="打卡记录不存在"
            )
        
        # 验证权限
        if check_in.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此打卡记录"
            )
        
        # 更新照片 URL
        check_in.photo_url = photo_url
        db.commit()
        db.refresh(check_in)
        
        logger.info("Photo uploaded for check-in: {}", check_in_id)
        
        return CheckInResponse.from_orm(check_in)
    
    @staticmethod
    def review_check_in(
        db: Session,
        check_in_id: str,
        reviewer_id: str,
        request: ReviewCheckInRequest
    ) -> CheckInResponse:
        """
        审核打卡记录
        
        Args:
            db: 数据库会话
            check_in_id: 打卡记录 ID
            reviewer_id: 审核者 ID
            request: 审核请求
            
        Returns:
            CheckInResponse: 审核后的打卡记录
            
        Raises:
            HTTPException: 打卡记录不存在或无权限
        """
        check_in = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
        if not check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="打卡记录不存在"
            )
        
        # 获取计划信息
        plan = db.query(BettingPlan).filter(BettingPlan.id == check_in.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联计划不存在"
            )
        
        # 验证审核者是对方参与者
        if check_in.user_id == plan.creator_id:
            # 打卡者是创建者,审核者应该是参与者
            if reviewer_id != plan.participant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有对方参与者可以审核"
                )
        elif check_in.user_id == plan.participant_id:
            # 打卡者是参与者,审核者应该是创建者
            if reviewer_id != plan.creator_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有对方参与者可以审核"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="打卡记录与计划不匹配"
            )
        
        # 更新审核状态
        check_in.review_status = request.review_status
        check_in.reviewer_id = reviewer_id
        check_in.review_comment = request.review_comment
        
        db.commit()
        db.refresh(check_in)
        
        logger.info(
            f"Check-in reviewed: id={check_in_id}, reviewer={reviewer_id}, "
            f"status={request.review_status}"
        )
        
        return CheckInResponse.from_orm(check_in)
    
    @staticmethod
    def get_check_in_history(
        db: Session,
        plan_id: str,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[CheckInResponse]:
        """
        获取打卡历史
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[CheckInResponse]: 打卡记录列表
        """
        check_ins = db.query(CheckIn).filter(
            and_(
                CheckIn.plan_id == plan_id,
                CheckIn.user_id == user_id
            )
        ).order_by(
            CheckIn.check_in_date.desc()
        ).limit(limit).offset(offset).all()
        
        return [CheckInResponse.from_orm(check_in) for check_in in check_ins]
    
    @staticmethod
    def get_progress(
        db: Session,
        plan_id: str,
        user_id: str
    ) -> ProgressStats:
        """
        计算进度统计
        
        Args:
            db: 数据库会话
            plan_id: 计划 ID
            user_id: 用户 ID
            
        Returns:
            ProgressStats: 进度统计
            
        Raises:
            HTTPException: 计划不存在或用户不是参与者
        """
        # 获取计划
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )
        
        # 确定用户的目标
        if plan.creator_id == user_id:
            initial_weight = plan.creator_initial_weight
            target_weight = plan.creator_target_weight
            target_weight_loss = plan.creator_target_weight_loss
        elif plan.participant_id == user_id:
            initial_weight = plan.participant_initial_weight
            target_weight = plan.participant_target_weight
            target_weight_loss = plan.participant_target_weight_loss
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您不是该计划的参与者"
            )
        
        # 获取所有打卡记录
        check_ins = db.query(CheckIn).filter(
            and_(
                CheckIn.plan_id == plan_id,
                CheckIn.user_id == user_id,
                CheckIn.review_status == ReviewStatus.APPROVED
            )
        ).order_by(CheckIn.check_in_date.asc()).all()
        
        # 计算当前体重和进度
        if not check_ins:
            current_weight = initial_weight
            weight_loss = 0.0
            progress_percentage = 0.0
        else:
            # 使用最新的打卡记录
            latest_check_in = check_ins[-1]
            current_weight = latest_check_in.weight
            weight_loss = initial_weight - current_weight
            
            # 计算进度百分比
            if target_weight_loss > 0:
                progress_percentage = (weight_loss / target_weight_loss) * 100
            else:
                progress_percentage = 0.0
            
            # 确保进度在 0-100 之间
            progress_percentage = max(0.0, min(100.0, progress_percentage))
        
        # 计算剩余天数
        days_remaining = (plan.end_date.date() - date.today()).days
        days_remaining = max(0, days_remaining)
        
        return ProgressStats(
            current_weight=current_weight,
            initial_weight=initial_weight,
            target_weight=target_weight,
            weight_loss=weight_loss,
            target_weight_loss=target_weight_loss,
            progress_percentage=progress_percentage,
            check_in_count=len(check_ins),
            days_remaining=days_remaining
        )
    
    @staticmethod
    def get_latest_weight(
        db: Session,
        user_id: str,
        plan_id: str
    ) -> Optional[float]:
        """
        获取用户在指定计划中的最新体重
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            plan_id: 计划 ID
            
        Returns:
            Optional[float]: 最新体重,如果没有打卡记录则返回 None
        """
        latest_check_in = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.plan_id == plan_id,
                CheckIn.review_status == ReviewStatus.APPROVED
            )
        ).order_by(CheckIn.check_in_date.desc()).first()
        
        if latest_check_in:
            return latest_check_in.weight
        
        return None
