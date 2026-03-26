# -*- coding: utf-8 -*-
"""
Social Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LeaderboardType(str, Enum):
    """Leaderboard type enum"""
    WEIGHT_LOSS = "weight_loss"
    CHECK_IN_STREAK = "check_in_streak"
    WIN_RATE = "win_rate"


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    user_id: str
    nickname: str
    value: float = Field(..., description="Metric value (weight loss, streak days, or win rate)")
    rank: int


class CommentRequest(BaseModel):
    """Create comment request"""
    content: str = Field(..., min_length=1, max_length=500, description="Comment content")


class CommentResponse(BaseModel):
    """Comment response"""
    id: str
    plan_id: str
    user_id: str
    user_nickname: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BadgeType(str, Enum):
    """Badge type enum"""
    FIRST_CHALLENGE = "first_challenge"
    WEEK_STREAK = "week_streak"
    MONTH_STREAK = "month_streak"
    WEIGHT_LOSS_MASTER = "weight_loss_master"
    CHAMPION = "champion"


class BadgeResponse(BaseModel):
    """Badge response"""
    id: str
    user_id: str
    badge_type: BadgeType
    badge_name: str
    badge_description: str
    earned_at: datetime
