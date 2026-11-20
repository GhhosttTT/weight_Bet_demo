# -*- coding: utf-8 -*-
"""
Notification Schemas
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    """Platform enum"""
    ANDROID = "android"
    IOS = "ios"


class NotificationType(str, Enum):
    """Notification type enum"""
    PLAN_INVITATION = "plan_invitation"
    PLAN_ACTIVATED = "plan_activated"
    SETTLEMENT_COMPLETED = "settlement_completed"
    CHECK_IN_REMINDER = "check_in_reminder"
    CHECK_IN_REVIEW = "check_in_review"
    PLAN_EXPIRED = "plan_expired"
    DISPUTE_SUBMITTED = "dispute_submitted"


class RegisterDeviceTokenRequest(BaseModel):
    """Register device token request"""
    token: str = Field(..., description="Device token")
    platform: Platform = Field(..., description="Platform (android/ios)")


class DeviceTokenResponse(BaseModel):
    """Device token response"""
    id: str
    user_id: str
    token: str
    platform: Platform
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SendNotificationRequest(BaseModel):
    """Send notification request"""
    user_id: str = Field(..., description="Target user ID")
    notification_type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Optional[dict] = Field(None, description="Additional data")


class NotificationResponse(BaseModel):
    """Notification response"""
    success: bool
    message: str
    failed_tokens: Optional[List[str]] = None
