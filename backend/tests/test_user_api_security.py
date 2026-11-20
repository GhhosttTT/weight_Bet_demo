import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from app.api.users import AuditLogQuery
from app.config import settings


def test_audit_log_query_has_bounded_pagination():
    assert AuditLogQuery(limit=500, offset=0).limit == 500
    with pytest.raises(ValidationError):
        AuditLogQuery(limit=501)
    with pytest.raises(ValidationError):
        AuditLogQuery(limit=0)
    with pytest.raises(ValidationError):
        AuditLogQuery(offset=-1)


def test_legacy_payment_method_binding_is_disabled_in_stripe_mode(monkeypatch):
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "stripe")
    with pytest.raises(HTTPException) as error:
        # API 层在访问数据库前就应阻断旧绑定入口，避免未经 Stripe 确认的
        # payment_method_id 被写入用户资料。
        from app.api.users import bind_payment_method
        bind_payment_method(
            user_id="user-1",
            request=type("Request", (), {"payment_method_id": "pm_unverified"})(),
            current_user_id="user-1",
            db=None,
        )
    assert error.value.status_code == 410
