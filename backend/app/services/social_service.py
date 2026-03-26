# -*- coding: utf-8 -*-
"""
Social Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from fastapi import HTTPException, status
from typing import List
import uuid
from datetime import datetime, timedelta, date
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.check_in import CheckIn
from app.models.settlement import Settlement
from app.models.comment import Comment
from app.models.badge import UserBadge, BadgeType
from app.schemas.social import (
    LeaderboardEntry,
    LeaderboardType,
    CommentRequest,
    CommentResponse,
    BadgeResponse
)
from app.logger import get_logger
from app.redis_client import redis_client as get_redis_client

logger = get_logger()


class SocialService:
    """Social service for leaderboards, comments, and badges"""
    
    BADGE_INFO = {
        BadgeType.FIRST_CHALLENGE: {
            "name": "First Challenge",
            "description": "Completed your first betting plan"
        },
        BadgeType.WEEK_STREAK: {
            "name": "Week Warrior",
            "description": "7 days check-in streak"
        },
        BadgeType.MONTH_STREAK: {
            "name": "Month Master",
            "description": "30 days check-in streak"
        },
        BadgeType.WEIGHT_LOSS_MASTER: {
            "name": "Weight Loss Master",
            "description": "Lost 10kg total"
        },
        BadgeType.CHAMPION: {
            "name": "Champion",
            "description": "80% win rate with 5+ plans"
        }
    }
    
    @staticmethod
    def get_weight_loss_leaderboard(
        db: Session,
        limit: int = 100
    ) -> List[LeaderboardEntry]:
        """
        Get weight loss leaderboard
        
        Args:
            db: Database session
            limit: Number of entries to return
            
        Returns:
            List[LeaderboardEntry]: Leaderboard entries
        """
        # Try to get from cache
        try:
            redis_client = get_redis_client
            cache_key = f"leaderboard:weight_loss:{limit}"
            
            if redis_client:
                cached = redis_client.get(cache_key)
                if cached:
                    import json
                    data = json.loads(cached)
                    return [LeaderboardEntry(**entry) for entry in data]
        except Exception as e:
            # Redis not available, continue without cache
            logger.warning("Redis cache unavailable: {}", e)
        
        # Calculate total weight loss for each user
        results = db.query(
            CheckIn.user_id,
            User.nickname,
            func.min(CheckIn.weight).label('min_weight'),
            func.max(CheckIn.weight).label('max_weight')
        ).join(
            User, CheckIn.user_id == User.id
        ).group_by(
            CheckIn.user_id, User.nickname
        ).all()
        
        # Calculate weight loss and sort
        leaderboard = []
        for user_id, nickname, min_weight, max_weight in results:
            if min_weight and max_weight:
                weight_loss = max_weight - min_weight
                if weight_loss > 0:
                    leaderboard.append({
                        "user_id": user_id,
                        "nickname": nickname,
                        "value": weight_loss
                    })
        
        leaderboard.sort(key=lambda x: x["value"], reverse=True)
        leaderboard = leaderboard[:limit]
        
        # Add ranks
        entries = [
            LeaderboardEntry(rank=i+1, **entry)
            for i, entry in enumerate(leaderboard)
        ]
        
        # Cache for 5 minutes
        try:
            if redis_client:
                import json
                redis_client.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps([e.model_dump() for e in entries])
                )
        except Exception as e:
            # Redis not available, continue without cache
            logger.warning("Redis cache write failed: {}", e)
        
        return entries
    
    @staticmethod
    def get_check_in_streak_leaderboard(
        db: Session,
        limit: int = 100
    ) -> List[LeaderboardEntry]:
        """
        Get check-in streak leaderboard
        
        Args:
            db: Database session
            limit: Number of entries to return
            
        Returns:
            List[LeaderboardEntry]: Leaderboard entries
        """
        # Try to get from cache
        try:
            redis_client = get_redis_client
            cache_key = f"leaderboard:check_in_streak:{limit}"
            
            if redis_client:
                cached = redis_client.get(cache_key)
                if cached:
                    import json
                    data = json.loads(cached)
                    return [LeaderboardEntry(**entry) for entry in data]
        except Exception as e:
            # Redis not available, continue without cache
            logger.warning("Redis cache unavailable: {}", e)
        
        # Get all users with check-ins
        users = db.query(User).all()
        leaderboard = []
        
        for user in users:
            # Get user's check-ins ordered by date
            check_ins = db.query(CheckIn).filter(
                CheckIn.user_id == user.id
            ).order_by(desc(CheckIn.check_in_date)).all()
            
            if not check_ins:
                continue
            
            # Calculate current streak
            streak = 0
            current_date = date.today()
            
            for check_in in check_ins:
                if check_in.check_in_date == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif check_in.check_in_date == current_date - timedelta(days=1):
                    streak += 1
                    current_date = check_in.check_in_date - timedelta(days=1)
                else:
                    break
            
            if streak > 0:
                leaderboard.append({
                    "user_id": user.id,
                    "nickname": user.nickname,
                    "value": float(streak)
                })
        
        leaderboard.sort(key=lambda x: x["value"], reverse=True)
        leaderboard = leaderboard[:limit]
        
        entries = [
            LeaderboardEntry(rank=i+1, **entry)
            for i, entry in enumerate(leaderboard)
        ]
        
        # Cache for 5 minutes
        try:
            if redis_client:
                import json
                redis_client.setex(
                    cache_key,
                    300,
                    json.dumps([e.model_dump() for e in entries])
                )
        except Exception as e:
            # Redis not available, continue without cache
            logger.warning("Redis cache write failed: {}", e)
        
        return entries
    
    @staticmethod
    def get_win_rate_leaderboard(
        db: Session,
        limit: int = 100
    ) -> List[LeaderboardEntry]:
        """
        Get win rate leaderboard
        
        Args:
            db: Database session
            limit: Number of entries to return
            
        Returns:
            List[LeaderboardEntry]: Leaderboard entries
        """
        # Try to get from cache
        try:
            redis_client = get_redis_client
            cache_key = f"leaderboard:win_rate:{limit}"
            
            if redis_client:
                cached = redis_client.get(cache_key)
                if cached:
                    import json
                    data = json.loads(cached)
                    return [LeaderboardEntry(**entry) for entry in data]
        except Exception as e:
            # Redis not available, continue without cache
            logger.warning("Redis cache unavailable: {}", e)
        
        # Get all users
        users = db.query(User).all()
        leaderboard = []
        
        for user in users:
            # Get completed plans
            completed_plans = db.query(BettingPlan).filter(
                and_(
                    BettingPlan.status == PlanStatus.COMPLETED,
                    (BettingPlan.creator_id == user.id) | (BettingPlan.participant_id == user.id)
                )
            ).all()
            
            if len(completed_plans) < 5:  # Minimum 5 plans
                continue
            
            # Count wins
            wins = 0
            for plan in completed_plans:
                settlement = db.query(Settlement).filter(
                    Settlement.plan_id == plan.id
                ).first()
                
                if settlement:
                    if plan.creator_id == user.id and settlement.creator_achieved:
                        wins += 1
                    elif plan.participant_id == user.id and settlement.participant_achieved:
                        wins += 1
            
            win_rate = (wins / len(completed_plans)) * 100
            
            leaderboard.append({
                "user_id": user.id,
                "nickname": user.nickname,
                "value": win_rate
            })
        
        leaderboard.sort(key=lambda x: x["value"], reverse=True)
        leaderboard = leaderboard[:limit]
        
        entries = [
            LeaderboardEntry(rank=i+1, **entry)
            for i, entry in enumerate(leaderboard)
        ]
        
        # Cache for 5 minutes
        try:
            if redis_client:
                import json
                redis_client.setex(
                    cache_key,
                    300,
                    json.dumps([e.model_dump() for e in entries])
                )
        except Exception as e:
            # Redis not available, continue without cache
            logger.warning("Redis cache write failed: {}", e)
        
        return entries
    
    @staticmethod
    def create_comment(
        db: Session,
        plan_id: str,
        user_id: str,
        request: CommentRequest
    ) -> CommentResponse:
        """
        Create a comment on a betting plan
        
        Args:
            db: Database session
            plan_id: Plan ID
            user_id: User ID
            request: Comment request
            
        Returns:
            CommentResponse: Comment response
        """
        # Verify plan exists
        plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create comment
        comment = Comment(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            user_id=user_id,
            content=request.content
        )
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        logger.info("User {} commented on plan {}", user_id, plan_id)
        
        return CommentResponse(
            id=comment.id,
            plan_id=comment.plan_id,
            user_id=comment.user_id,
            user_nickname=user.nickname,
            content=comment.content,
            created_at=comment.created_at
        )
    
    @staticmethod
    def get_comments(
        db: Session,
        plan_id: str,
        limit: int = 50
    ) -> List[CommentResponse]:
        """
        Get comments for a betting plan
        
        Args:
            db: Database session
            plan_id: Plan ID
            limit: Number of comments to return
            
        Returns:
            List[CommentResponse]: List of comments
        """
        comments = db.query(Comment, User.nickname).join(
            User, Comment.user_id == User.id
        ).filter(
            Comment.plan_id == plan_id
        ).order_by(
            desc(Comment.created_at)
        ).limit(limit).all()
        
        return [
            CommentResponse(
                id=comment.id,
                plan_id=comment.plan_id,
                user_id=comment.user_id,
                user_nickname=nickname,
                content=comment.content,
                created_at=comment.created_at
            )
            for comment, nickname in comments
        ]
    
    @staticmethod
    def award_badge(
        db: Session,
        user_id: str,
        badge_type: BadgeType
    ) -> BadgeResponse:
        """
        Award a badge to a user
        
        Args:
            db: Database session
            user_id: User ID
            badge_type: Badge type
            
        Returns:
            BadgeResponse: Badge response
        """
        # Check if user already has this badge
        existing = db.query(UserBadge).filter(
            and_(
                UserBadge.user_id == user_id,
                UserBadge.badge_type == badge_type
            )
        ).first()
        
        if existing:
            badge_info = SocialService.BADGE_INFO[badge_type]
            return BadgeResponse(
                id=existing.id,
                user_id=existing.user_id,
                badge_type=existing.badge_type,
                badge_name=badge_info["name"],
                badge_description=badge_info["description"],
                earned_at=existing.earned_at
            )
        
        # Create new badge
        badge = UserBadge(
            id=str(uuid.uuid4()),
            user_id=user_id,
            badge_type=badge_type
        )
        
        db.add(badge)
        db.commit()
        db.refresh(badge)
        
        logger.info("Awarded badge {} to user {}", badge_type, user_id)
        
        badge_info = SocialService.BADGE_INFO[badge_type]
        return BadgeResponse(
            id=badge.id,
            user_id=badge.user_id,
            badge_type=badge.badge_type,
            badge_name=badge_info["name"],
            badge_description=badge_info["description"],
            earned_at=badge.earned_at
        )
    
    @staticmethod
    def get_user_badges(
        db: Session,
        user_id: str
    ) -> List[BadgeResponse]:
        """
        Get all badges for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List[BadgeResponse]: List of badges
        """
        badges = db.query(UserBadge).filter(
            UserBadge.user_id == user_id
        ).order_by(desc(UserBadge.earned_at)).all()
        
        return [
            BadgeResponse(
                id=badge.id,
                user_id=badge.user_id,
                badge_type=badge.badge_type,
                badge_name=SocialService.BADGE_INFO[badge.badge_type]["name"],
                badge_description=SocialService.BADGE_INFO[badge.badge_type]["description"],
                earned_at=badge.earned_at
            )
            for badge in badges
        ]
    
    @staticmethod
    def check_and_award_badges(db: Session, user_id: str):
        """
        Check and award badges to a user based on their achievements
        
        Args:
            db: Database session
            user_id: User ID
        """
        # Check first challenge
        completed_plans = db.query(BettingPlan).filter(
            and_(
                BettingPlan.status == PlanStatus.COMPLETED,
                (BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)
            )
        ).count()
        
        if completed_plans >= 1:
            SocialService.award_badge(db, user_id, BadgeType.FIRST_CHALLENGE)
        
        # Check streak badges
        check_ins = db.query(CheckIn).filter(
            CheckIn.user_id == user_id
        ).order_by(desc(CheckIn.check_in_date)).all()
        
        if check_ins:
            streak = 1
            current_date = check_ins[0].check_in_date
            
            for i in range(1, len(check_ins)):
                if check_ins[i].check_in_date == current_date - timedelta(days=1):
                    streak += 1
                    current_date = check_ins[i].check_in_date
                else:
                    break
            
            if streak >= 7:
                SocialService.award_badge(db, user_id, BadgeType.WEEK_STREAK)
            if streak >= 30:
                SocialService.award_badge(db, user_id, BadgeType.MONTH_STREAK)
        
        # Check weight loss master
        if check_ins:
            weights = [ci.weight for ci in check_ins]
            total_loss = max(weights) - min(weights)
            if total_loss >= 10:
                SocialService.award_badge(db, user_id, BadgeType.WEIGHT_LOSS_MASTER)
        
        # Check champion
        if completed_plans >= 5:
            wins = 0
            plans = db.query(BettingPlan).filter(
                and_(
                    BettingPlan.status == PlanStatus.COMPLETED,
                    (BettingPlan.creator_id == user_id) | (BettingPlan.participant_id == user_id)
                )
            ).all()
            
            for plan in plans:
                settlement = db.query(Settlement).filter(
                    Settlement.plan_id == plan.id
                ).first()
                
                if settlement:
                    if plan.creator_id == user_id and settlement.creator_achieved:
                        wins += 1
                    elif plan.participant_id == user_id and settlement.participant_achieved:
                        wins += 1
            
            win_rate = (wins / completed_plans) * 100
            if win_rate >= 80:
                SocialService.award_badge(db, user_id, BadgeType.CHAMPION)
