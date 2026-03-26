# -*- coding: utf-8 -*-
"""
Notification API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
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
    # TODO: Add admin check
    return NotificationService.send_notification(db, request)


@router.post("/notifications/scheduled-reminders")
async def send_scheduled_check_in_reminders(
    db: Session = Depends(get_db)
):
    """
    Send daily check-in reminders (scheduled task endpoint)
    
    Note: This endpoint should be called by a scheduler and needs proper authentication
    
    Args:
        db: Database session
        
    Returns:
        dict: Statistics about sent reminders
    """
    # TODO: Add API key or other authentication mechanism
    return NotificationService.send_daily_check_in_reminders(db)
