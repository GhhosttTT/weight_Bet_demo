# -*- coding: utf-8 -*-
"""
Notification Service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
import uuid
from datetime import datetime
from app.models.device_token import DeviceToken, Platform
from app.models.user import User
from app.schemas.notification import (
    RegisterDeviceTokenRequest,
    DeviceTokenResponse,
    SendNotificationRequest,
    NotificationResponse,
    NotificationType
)
from app.logger import get_logger

logger = get_logger()


class NotificationService:
    """Notification service for managing push notifications"""
    
    @staticmethod
    def register_device_token(
        db: Session,
        user_id: str,
        request: RegisterDeviceTokenRequest
    ) -> DeviceTokenResponse:
        """
        Register device token for push notifications
        
        Args:
            db: Database session
            user_id: User ID
            request: Register device token request
            
        Returns:
            DeviceTokenResponse: Device token response
        """
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if token already exists
        existing_token = db.query(DeviceToken).filter(
            DeviceToken.token == request.token
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.user_id = user_id
            existing_token.platform = request.platform
            existing_token.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_token)
            return DeviceTokenResponse.model_validate(existing_token)
        
        # Create new token
        device_token = DeviceToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token=request.token,
            platform=request.platform
        )
        
        db.add(device_token)
        db.commit()
        db.refresh(device_token)
        
        logger.info("Registered device token for user {}, platform: {}", user_id, request.platform)
        
        return DeviceTokenResponse.model_validate(device_token)
    
    @staticmethod
    def get_user_device_tokens(
        db: Session,
        user_id: str
    ) -> List[DeviceToken]:
        """
        Get all device tokens for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List[DeviceToken]: List of device tokens
        """
        return db.query(DeviceToken).filter(
            DeviceToken.user_id == user_id
        ).all()
    
    @staticmethod
    def delete_device_token(
        db: Session,
        user_id: str,
        token: str
    ) -> bool:
        """
        Delete a device token
        
        Args:
            db: Database session
            user_id: User ID
            token: Device token
            
        Returns:
            bool: True if deleted, False if not found
        """
        device_token = db.query(DeviceToken).filter(
            DeviceToken.user_id == user_id,
            DeviceToken.token == token
        ).first()
        
        if not device_token:
            return False
        
        db.delete(device_token)
        db.commit()
        
        logger.info("Deleted device token for user {}", user_id)
        
        return True
    
    @staticmethod
    def send_notification(
        db: Session,
        request: SendNotificationRequest
    ) -> NotificationResponse:
        """
        Send push notification to a user
        
        Args:
            db: Database session
            request: Send notification request
            
        Returns:
            NotificationResponse: Notification response
        """
        # Get user's device tokens
        device_tokens = NotificationService.get_user_device_tokens(db, request.user_id)
        
        if not device_tokens:
            logger.warning("No device tokens found for user {}", request.user_id)
            return NotificationResponse(
                success=False,
                message="No device tokens registered for user"
            )
        
        # TODO: Implement actual FCM/APNs integration
        # For now, just log the notification
        logger.info(
            "Sending notification to user {}: type={}, title={}",
            request.user_id, request.notification_type, request.title
        )
        
        # In production, you would:
        # 1. For Android tokens: Use Firebase Cloud Messaging
        # 2. For iOS tokens: Use Apple Push Notification Service
        # 3. Handle failed tokens and remove them from database
        
        return NotificationResponse(
            success=True,
            message=f"Notification sent to {len(device_tokens)} device(s)"
        )
    
    @staticmethod
    def send_plan_invitation_notification(
        db: Session,
        user_id: str,
        plan_id: str,
        creator_name: str
    ):
        """
        Send plan invitation notification
        
        Args:
            db: Database session
            user_id: Target user ID
            plan_id: Plan ID
            creator_name: Creator's name
        """
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.PLAN_INVITATION,
            title="New Betting Plan Invitation",
            body="{} invited you to join a weight loss challenge!".format(creator_name),
            data={"plan_id": plan_id}
        )
        return NotificationService.send_notification(db, request)
    
    @staticmethod
    def send_plan_activated_notification(
        db: Session,
        user_id: str,
        plan_id: str
    ):
        """
        Send plan activated notification
        
        Args:
            db: Database session
            user_id: Target user ID
            plan_id: Plan ID
        """
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.PLAN_ACTIVATED,
            title="Plan Activated",
            body="Your weight loss challenge has started! Good luck!",
            data={"plan_id": plan_id}
        )
        return NotificationService.send_notification(db, request)
    
    @staticmethod
    def send_settlement_notification(
        db: Session,
        user_id: str,
        plan_id: str,
        amount: float,
        achieved: bool
    ):
        """
        Send settlement notification
        
        Args:
            db: Database session
            user_id: Target user ID
            plan_id: Plan ID
            amount: Settlement amount
            achieved: Whether user achieved goal
        """
        if achieved:
            title = "Congratulations!"
            body = "You achieved your goal and won ${}!".format(amount)
        else:
            title = "Challenge Completed"
            body = "Challenge ended. You received ${}.".format(amount)
        
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.SETTLEMENT_COMPLETED,
            title=title,
            body=body,
            data={"plan_id": plan_id, "amount": amount}
        )
        return NotificationService.send_notification(db, request)
    
    @staticmethod
    def send_check_in_reminder(
        db: Session,
        user_id: str,
        plan_id: str
    ):
        """
        Send check-in reminder notification
        
        Args:
            db: Database session
            user_id: Target user ID
            plan_id: Plan ID
        """
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.CHECK_IN_REMINDER,
            title="Daily Check-in Reminder",
            body="Don't forget to log your weight today!",
            data={"plan_id": plan_id}
        )
        return NotificationService.send_notification(db, request)
    
    @staticmethod
    def send_plan_expired_notification(
        db: Session,
        user_id: str,
        plan_id: str
    ):
        """
        Send plan expired notification
        
        Args:
            db: Database session
            user_id: Target user ID
            plan_id: Plan ID
        """
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.PLAN_EXPIRED,
            title="Plan Expired",
            body="Your weight loss challenge has expired. Please check the results.",
            data={"plan_id": plan_id}
        )
        return NotificationService.send_notification(db, request)
    
    @staticmethod
    def send_daily_check_in_reminders(db: Session) -> dict:
        """
        Send check-in reminders to all users with active plans who haven't checked in today
        
        Args:
            db: Database session
            
        Returns:
            dict: Statistics about sent reminders
        """
        from app.models.betting_plan import BettingPlan, PlanStatus
        from app.models.check_in import CheckIn
        from datetime import date
        
        # Get all active plans
        active_plans = db.query(BettingPlan).filter(
            BettingPlan.status == PlanStatus.ACTIVE
        ).all()
        
        sent_count = 0
        failed_count = 0
        
        for plan in active_plans:
            # Check if creator has checked in today
            creator_check_in = db.query(CheckIn).filter(
                CheckIn.user_id == plan.creator_id,
                CheckIn.plan_id == plan.id,
                CheckIn.check_in_date == date.today()
            ).first()
            
            if not creator_check_in:
                try:
                    NotificationService.send_check_in_reminder(
                        db, plan.creator_id, plan.id
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error("Failed to send reminder to creator {}: {}", plan.creator_id, e)
                    failed_count += 1
            
            # Check if participant has checked in today
            if plan.participant_id:
                participant_check_in = db.query(CheckIn).filter(
                    CheckIn.user_id == plan.participant_id,
                    CheckIn.plan_id == plan.id,
                    CheckIn.check_in_date == date.today()
                ).first()
                
                if not participant_check_in:
                    try:
                        NotificationService.send_check_in_reminder(
                            db, plan.participant_id, plan.id
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error("Failed to send reminder to participant {}: {}", plan.participant_id, e)
                        failed_count += 1
        
        logger.info("Sent {} check-in reminders, {} failed", sent_count, failed_count)
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total_plans": len(active_plans)
        }
