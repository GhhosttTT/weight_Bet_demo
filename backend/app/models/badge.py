# -*- coding: utf-8 -*-
"""
Badge Model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class BadgeType(str, enum.Enum):
    """Badge type enum"""
    FIRST_CHALLENGE = "first_challenge"
    WEEK_STREAK = "week_streak"
    MONTH_STREAK = "month_streak"
    WEIGHT_LOSS_MASTER = "weight_loss_master"
    CHAMPION = "champion"


class UserBadge(Base):
    """User badge model"""
    __tablename__ = "user_badges"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    badge_type = Column(SQLEnum(BadgeType), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
