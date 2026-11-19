import pytest
from pydantic import ValidationError

from app.api.users import AuditLogQuery


def test_audit_log_query_has_bounded_pagination():
    assert AuditLogQuery(limit=500, offset=0).limit == 500
    with pytest.raises(ValidationError):
        AuditLogQuery(limit=501)
    with pytest.raises(ValidationError):
        AuditLogQuery(limit=0)
    with pytest.raises(ValidationError):
        AuditLogQuery(offset=-1)
