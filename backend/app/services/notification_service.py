# -*- coding: utf-8 -*-
"""
Notification Service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
import uuid
import time
from datetime import datetime
from pathlib import Path
import httpx
from jose import jwt
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import service_account
from app.config import settings
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
        
        failed_tokens = []
        normalized_data = NotificationService._normalized_data(request)
        request = request.model_copy(update={"data": normalized_data})
        sent_count = 0
        for device in device_tokens:
            try:
                if device.platform == Platform.ANDROID:
                    sent = NotificationService._send_fcm(device.token, request)
                else:
                    sent = NotificationService._send_apns(device.token, request)
                if sent:
                    sent_count += 1
            except NotificationService.InvalidDeviceToken:
                failed_tokens.append(device.token)
                db.delete(device)
            except NotificationService.ProviderNotConfigured:
                failed_tokens.append(device.token)
            except Exception as error:
                failed_tokens.append(device.token)
                logger.error("Push notification failed for platform {}: {}", device.platform, error)

        if failed_tokens:
            db.commit()
        success = sent_count > 0 and not failed_tokens
        return NotificationResponse(
            success=success,
            message=f"已发送 {sent_count}/{len(device_tokens)} 台设备" if sent_count else "推送未发送，请检查推送服务配置",
            failed_tokens=failed_tokens,
        )

    class ProviderNotConfigured(Exception):
        """对应平台的推送凭据未配置。"""

    class InvalidDeviceToken(Exception):
        """推送服务确认令牌失效。"""

    @staticmethod
    def _normalized_data(request: SendNotificationRequest) -> dict:
        """统一移动端点击跳转所需的 type/relatedId 字段。"""
        data = dict(request.data or {})
        client_types = {
            NotificationType.PLAN_INVITATION: "invite",
            NotificationType.PLAN_ACTIVATED: "plan_active",
            NotificationType.SETTLEMENT_COMPLETED: "settlement",
            NotificationType.CHECK_IN_REMINDER: "check_in_reminder",
            NotificationType.PLAN_EXPIRED: "plan_expired",
        }
        data.setdefault("type", client_types.get(request.notification_type, request.notification_type.value))
        related_id = data.get("relatedId") or data.get("plan_id") or data.get("settlement_id")
        if related_id is not None:
            data.setdefault("relatedId", str(related_id))
        return data

    @staticmethod
    def _send_fcm(token: str, request: SendNotificationRequest) -> bool:
        """通过 FCM HTTP v1 发送，使用服务账号 OAuth2，不记录令牌或访问令牌。"""
        credentials_path = Path(settings.FIREBASE_CREDENTIALS_PATH)
        if not settings.FCM_PROJECT_ID or not credentials_path.is_file():
            raise NotificationService.ProviderNotConfigured()
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/firebase.messaging"],
        )
        credentials.refresh(GoogleAuthRequest())
        data = {str(key): str(value) for key, value in (request.data or {}).items()}
        data["notification_type"] = request.notification_type.value
        payload = {
            "message": {
                "token": token,
                "notification": {"title": request.title, "body": request.body},
                "data": data,
            }
        }
        response = httpx.post(
            f"https://fcm.googleapis.com/v1/projects/{settings.FCM_PROJECT_ID}/messages:send",
            headers={"Authorization": f"Bearer {credentials.token}"},
            json=payload,
            timeout=10.0,
        )
        if response.status_code in (400, 404):
            error_text = response.text.upper()
            if "UNREGISTERED" in error_text or "INVALID_ARGUMENT" in error_text:
                raise NotificationService.InvalidDeviceToken()
        response.raise_for_status()
        return True

    @staticmethod
    def _send_apns(token: str, request: SendNotificationRequest) -> bool:
        """通过 APNs Provider API 发送，使用 ES256 token 认证。"""
        key_path = Path(settings.APNS_PRIVATE_KEY_PATH)
        if not all((settings.APNS_KEY_ID, settings.APNS_TEAM_ID, settings.APNS_BUNDLE_ID)) or not key_path.is_file():
            raise NotificationService.ProviderNotConfigured()
        private_key = key_path.read_text(encoding="utf-8")
        provider_token = jwt.encode(
            {"iss": settings.APNS_TEAM_ID, "iat": int(time.time())},
            private_key,
            algorithm="ES256",
            headers={"kid": settings.APNS_KEY_ID},
        )
        data = request.data or {}
        payload = {
            "aps": {"alert": {"title": request.title, "body": request.body}, "sound": "default"},
            **data,
        }
        host = "https://api.sandbox.push.apple.com" if settings.APNS_USE_SANDBOX else "https://api.push.apple.com"
        response = httpx.post(
            f"{host}/3/device/{token}",
            headers={
                "authorization": f"bearer {provider_token}",
                "apns-topic": settings.APNS_BUNDLE_ID,
                "apns-push-type": "alert",
                "apns-priority": "10",
            },
            json=payload,
            timeout=10.0,
        )
        if response.status_code in (400, 410):
            try:
                reason = response.json().get("reason", "")
            except ValueError:
                reason = ""
            if reason in ("BadDeviceToken", "Unregistered", "DeviceTokenNotForTopic"):
                raise NotificationService.InvalidDeviceToken()
        response.raise_for_status()
        return True
    
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
    def send_plan_invitation_accepted_notification(db: Session, user_id: str, plan_id: str):
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.PLAN_ACTIVATED,
            title="对赌计划已接受",
            body="对方已接受你的减重挑战，请确认计划后开始。",
            data={"plan_id": plan_id},
        )
        return NotificationService.send_notification(db, request)

    @staticmethod
    def send_plan_confirmed_notification(db: Session, user_id: str, plan_id: str):
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.PLAN_ACTIVATED,
            title="对赌计划已生效",
            body="你的减重挑战已经开始，记得按时打卡。",
            data={"plan_id": plan_id},
        )
        return NotificationService.send_notification(db, request)

    @staticmethod
    def send_plan_rejected_notification(db: Session, user_id: str, plan_id: str):
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.PLAN_EXPIRED,
            title="对赌计划未通过",
            body="该计划已被拒绝，相关资金将按规则处理。",
            data={"plan_id": plan_id},
        )
        return NotificationService.send_notification(db, request)

    @staticmethod
    def send_dispute_submitted_notification(
        db: Session,
        admin_user_id: str,
        dispute_id: str,
        settlement_id: str,
    ):
        request = SendNotificationRequest(
            user_id=admin_user_id,
            notification_type=NotificationType.DISPUTE_SUBMITTED,
            title="收到新的结算争议",
            body="有一条结算争议等待后台处理。",
            data={"dispute_id": dispute_id, "settlement_id": settlement_id},
        )
        return NotificationService.send_notification(db, request)

    @staticmethod
    def send_dispute_status_notification(
        db: Session,
        user_id: str,
        dispute_id: str,
        settlement_id: str,
        dispute_status: str,
        admin_notes: Optional[str] = None,
    ):
        status_copy = {
            "under_review": "结算争议已进入审核",
            "resolved": "结算争议已处理",
            "rejected": "结算争议未通过",
        }.get(dispute_status, "结算争议状态已更新")
        request = SendNotificationRequest(
            user_id=user_id,
            notification_type=NotificationType.DISPUTE_UPDATED,
            title=status_copy,
            body=admin_notes.strip() if admin_notes and admin_notes.strip() else "请打开应用查看最新处理结果。",
            data={
                "dispute_id": dispute_id,
                "settlement_id": settlement_id,
                "status": dispute_status,
                "admin_notes": admin_notes or "",
            },
        )
        return NotificationService.send_notification(db, request)
    
    @staticmethod
    def send_settlement_notification(
        db: Session,
        user_id: str,
        plan_id: str,
        amount: float,
        achieved: bool,
        settlement_id: Optional[str] = None,
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
            data={"plan_id": plan_id, "settlement_id": settlement_id or plan_id, "amount": amount}
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
