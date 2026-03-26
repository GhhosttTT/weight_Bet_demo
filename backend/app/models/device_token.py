# -*- coding: utf-8 -*-
"""
Device Token Model
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class Platform(str, enum.Enum):
    """Platform enum"""
    ANDROID = "android"
    IOS = "ios"


class DeviceToken(Base):
    """Device token model for push notifications"""
    __tablename__ = "device_tokens"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, nullable=False, unique=True)
    platform = Column(SQLEnum(Platform), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
