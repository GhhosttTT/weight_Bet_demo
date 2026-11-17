# -*- coding: utf-8 -*-
"""
Notification API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from typing import Optional
import secrets
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    RegisterDeviceTokenRequest,
    DeviceTokenResponse,
    SendNotificationRequest,
    NotificationResponse
)
from app.logger import get_logger
from app.config import settings

logger = get_logger()

router = APIRouter()


@router.post("/notifications/register", response_model=DeviceTokenResponse)
async def register_device_token(
    request: RegisterDeviceTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register device token for push notifications
    
    Args:
        request: Register device token request
        db: Database session
        current_user: Current user
        
    Returns:
        DeviceTokenResponse: Device token response
    """
    return NotificationService.register_device_token(
        db,
        current_user.id,
        request
    )


@router.delete("/notifications/token/{token}")
async def delete_device_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a device token
    
    Args:
        token: Device token
        db: Database session
        current_user: Current user
        
    Returns:
        dict: Success message
    """
    success = NotificationService.delete_device_token(
        db,
        current_user.id,
        token
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    
    return {"message": "Device token deleted successfully"}


@router.post("/notifications/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a push notification (admin/testing only)
    
    Args:
        request: Send notification request
        db: Database session
        current_user: Current user
        
    Returns:
        NotificationResponse: Notification response
    """
    # 当前 User 模型没有管理员/角色字段，不能把普通登录身份当作管理员。
    # 系统内部通知由 NotificationService 直接调用；公开 API 仅允许用户
    # 操作自己的通知目标，避免借接口向任意用户发送消息。
    if request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前账号无权向其他用户发送通知"
        )
    return NotificationService.send_notification(db, request)


@router.post("/notifications/scheduled-reminders")
async def send_scheduled_check_in_reminders(
    db: Session = Depends(get_db),
    scheduler_key: Optional[str] = Header(default=None, alias="X-Scheduler-Key")
):
    """
    Send daily check-in reminders (scheduled task endpoint)
    
    Note: This endpoint requires the configured scheduler key.
    
    Args:
        db: Database session
        
    Returns:
        dict: Statistics about sent reminders
    """
    if not settings.SCHEDULER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="定时任务密钥未配置"
        )
    if not scheduler_key or not secrets.compare_digest(scheduler_key, settings.SCHEDULER_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权执行定时提醒任务"
        )
    return NotificationService.send_daily_check_in_reminders(db)
