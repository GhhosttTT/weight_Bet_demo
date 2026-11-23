"""推送供应商适配器测试，不访问真实 FCM/APNs。"""

from types import SimpleNamespace

import pytest

from app.config import settings
from app.schemas.notification import NotificationType, SendNotificationRequest
from app.services.notification_service import NotificationService


def _request():
    return SendNotificationRequest(
        user_id="user-1",
        notification_type=NotificationType.PLAN_INVITATION,
        title="计划邀请",
        body="你收到一个邀请",
        data={"plan_id": "plan-1"},
    )


def test_fcm_delivery_uses_http_v1_without_logging_token(tmp_path, monkeypatch):
    credentials_file = tmp_path / "service-account.json"
    credentials_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(settings, "FIREBASE_CREDENTIALS_PATH", str(credentials_file))
    monkeypatch.setattr(settings, "FCM_PROJECT_ID", "weight-bet")

    credentials = SimpleNamespace(token="oauth-token", refresh=lambda request: None)
    monkeypatch.setattr(
        "app.services.notification_service.service_account.Credentials.from_service_account_file",
        lambda *args, **kwargs: credentials,
    )

    response = SimpleNamespace(status_code=200, text="", raise_for_status=lambda: None)
    calls = []
    monkeypatch.setattr(
        "app.services.notification_service.httpx.post",
        lambda url, **kwargs: calls.append((url, kwargs)) or response,
    )

    assert NotificationService._send_fcm("device-token", _request()) is True
    assert calls[0][0].endswith("/projects/weight-bet/messages:send")
    assert calls[0][1]["json"]["message"]["token"] == "device-token"
    assert calls[0][1]["json"]["message"]["data"]["notification_type"] == "plan_invitation"


def test_invalid_provider_token_is_classified_for_cleanup(monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_CREDENTIALS_PATH", "service-account.json")
    monkeypatch.setattr(settings, "FCM_PROJECT_ID", "weight-bet")
    monkeypatch.setattr(
        "app.services.notification_service.Path.is_file",
        lambda self: True,
    )
    credentials = SimpleNamespace(token="oauth-token", refresh=lambda request: None)
    monkeypatch.setattr(
        "app.services.notification_service.service_account.Credentials.from_service_account_file",
        lambda *args, **kwargs: credentials,
    )
    response = SimpleNamespace(
        status_code=404,
        text='{"error":{"status":"UNREGISTERED"}}',
        raise_for_status=lambda: None,
    )
    monkeypatch.setattr("app.services.notification_service.httpx.post", lambda *args, **kwargs: response)

    with pytest.raises(NotificationService.InvalidDeviceToken):
        NotificationService._send_fcm("stale-token", _request())


def test_apns_delivery_builds_alert_payload(tmp_path, monkeypatch):
    key_file = tmp_path / "AuthKey.p8"
    key_file.write_text("private-key", encoding="utf-8")
    monkeypatch.setattr(settings, "APNS_KEY_ID", "KEY123")
    monkeypatch.setattr(settings, "APNS_TEAM_ID", "TEAM123")
    monkeypatch.setattr(settings, "APNS_BUNDLE_ID", "com.weightloss.betting")
    monkeypatch.setattr(settings, "APNS_PRIVATE_KEY_PATH", str(key_file))
    monkeypatch.setattr("app.services.notification_service.jwt.encode", lambda *args, **kwargs: "provider-jwt")

    response = SimpleNamespace(status_code=200, text="", raise_for_status=lambda: None)
    calls = []
    monkeypatch.setattr(
        "app.services.notification_service.httpx.post",
        lambda url, **kwargs: calls.append((url, kwargs)) or response,
    )

    assert NotificationService._send_apns("device-token", _request()) is True
    assert calls[0][0].endswith("/3/device/device-token")
    assert calls[0][1]["json"]["aps"]["alert"]["title"] == "计划邀请"


def test_dispute_notification_targets_admin_with_related_ids(monkeypatch):
    captured = []

    def capture(db, request):
        captured.append(request)
        return SimpleNamespace(success=True)

    monkeypatch.setattr(NotificationService, "send_notification", capture)
    NotificationService.send_dispute_submitted_notification(
        object(), "admin-1", "dispute-1", "settlement-1"
    )

    assert captured[0].user_id == "admin-1"
    assert captured[0].notification_type == NotificationType.DISPUTE_SUBMITTED
    assert captured[0].data == {"dispute_id": "dispute-1", "settlement_id": "settlement-1"}


def test_dispute_status_notification_targets_user_with_status_and_notes(monkeypatch):
    captured = []

    def capture(db, request):
        captured.append(request)
        return SimpleNamespace(success=True)

    monkeypatch.setattr(NotificationService, "send_notification", capture)
    NotificationService.send_dispute_status_notification(
        object(), "user-1", "dispute-1", "settlement-1", "resolved", "已核实并完成处理"
    )

    assert captured[0].user_id == "user-1"
    assert captured[0].notification_type == NotificationType.DISPUTE_UPDATED
    assert captured[0].title == "结算争议已处理"
    assert captured[0].body == "已核实并完成处理"
    assert captured[0].data == {
        "dispute_id": "dispute-1",
        "settlement_id": "settlement-1",
        "status": "resolved",
        "admin_notes": "已核实并完成处理",
    }
