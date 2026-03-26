# -*- coding: utf-8 -*-
"""
Social API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.betting_plan import BettingPlan
from app.services.social_service import SocialService
from app.schemas.social import (
    LeaderboardEntry,
    LeaderboardType,
    CommentRequest,
    CommentResponse,
    BadgeResponse
)
from app.logger import get_logger

logger = get_logger()

router = APIRouter()


@router.get("/leaderboard/{leaderboard_type}", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    leaderboard_type: LeaderboardType,
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard
    
    Args:
        leaderboard_type: Type of leaderboard
        limit: Number of entries to return
        db: Database session
        
    Returns:
        List[LeaderboardEntry]: Leaderboard entries
    """
    if leaderboard_type == LeaderboardType.WEIGHT_LOSS:
        return SocialService.get_weight_loss_leaderboard(db, limit)
    elif leaderboard_type == LeaderboardType.CHECK_IN_STREAK:
        return SocialService.get_check_in_streak_leaderboard(db, limit)
    elif leaderboard_type == LeaderboardType.WIN_RATE:
        return SocialService.get_win_rate_leaderboard(db, limit)


@router.post("/plans/{plan_id}/comments", response_model=CommentResponse)
async def create_comment(
    plan_id: str,
    request: CommentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a comment on a betting plan
    
    Args:
        plan_id: Plan ID
        request: Comment request
        db: Database session
        current_user: Current user
        
    Returns:
        CommentResponse: Comment response
    """
    return SocialService.create_comment(db, plan_id, current_user.id, request)


@router.get("/plans/{plan_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    plan_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get comments for a betting plan
    
    Args:
        plan_id: Plan ID
        limit: Number of comments to return
        db: Database session
        
    Returns:
        List[CommentResponse]: List of comments
    """
    return SocialService.get_comments(db, plan_id, limit)


@router.get("/users/{user_id}/badges", response_model=List[BadgeResponse])
async def get_user_badges(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all badges for a user
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List[BadgeResponse]: List of badges
    """
    return SocialService.get_user_badges(db, user_id)


@router.post("/users/{user_id}/check-badges")
async def check_and_award_badges(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check and award badges to a user
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current user
        
    Returns:
        dict: Success message
    """
    # Only allow users to check their own badges
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only check your own badges"
        )
    
    SocialService.check_and_award_badges(db, user_id)
    return {"message": "Badges checked and awarded"}
