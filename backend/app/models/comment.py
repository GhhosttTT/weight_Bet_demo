# -*- coding: utf-8 -*-
"""
Comment Model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class Comment(Base):
    """Comment model for betting plans"""
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey("betting_plans.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
