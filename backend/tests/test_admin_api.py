"""后台管理 API 的权限、查询和更新边界测试。"""
from datetime import datetime, timedelta
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (
    User, Gender, BettingPlan, PlanStatus, CheckIn, ReviewStatus,
    Settlement, Dispute, DisputeStatus,
)
from app.utils.security import create_access_token, create_refresh_token, hash_password


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def admin_context():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_db
    db = Session()
    admin = User(
        id="admin-user",
        email="admin@example.com",
        password_hash=hash_password("secret"),
        nickname="运营管理员",
        gender=Gender.OTHER,
        age=30,
        height=170,
        current_weight=65,
        role="admin",
    )
    member = User(
        id="member-user",
        email="member@example.com",
        password_hash=hash_password("secret"),
        nickname="普通用户",
        gender=Gender.OTHER,
        age=25,
        height=170,
        current_weight=70,
        role="user",
    )
    db.add_all([admin, member])
    db.commit()
    admin_id = admin.id
    member_id = member.id
    db.close()
    client = TestClient(app)
    yield {
        "client": client,
        "admin": {"Authorization": f"Bearer {create_access_token({'sub': admin_id})}"},
        "member": {"Authorization": f"Bearer {create_access_token({'sub': member_id})}"},
    }
    client.close()
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


def test_all_admin_reads_require_admin_role(admin_context):
    client = admin_context["client"]
    headers = admin_context["member"]
    for path in (
        "/api/admin/dashboard",
        "/api/admin/users",
        "/api/admin/plans",
        "/api/admin/check-ins/pending",
        "/api/admin/disputes",
        "/api/admin/settlements",
        "/api/admin/transactions",
        "/api/admin/balances",
        "/api/admin/audit-logs",
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 403, path


def test_admin_rejects_refresh_and_invalid_tokens(admin_context):
    client = admin_context["client"]
    refresh_headers = {
        "Authorization": f"Bearer {create_refresh_token({'sub': 'admin-user'})}"
    }
    assert client.get("/api/admin/dashboard", headers=refresh_headers).status_code == 401
    assert client.get(
        "/api/admin/dashboard",
        headers={"Authorization": "Bearer tampered-token"},
    ).status_code == 401


def test_demoted_admin_loses_access_without_reissuing_token(admin_context):
    db = Session()
    db.query(User).filter(User.id == "admin-user").update({"role": "user"})
    db.commit()
    db.close()
    response = admin_context["client"].get(
        "/api/admin/dashboard",
        headers=admin_context["admin"],
    )
    assert response.status_code == 403


def test_admin_can_read_all_business_queues(admin_context):
    client = admin_context["client"]
    headers = admin_context["admin"]
    assert client.get("/api/admin/dashboard", headers=headers).status_code == 200
    assert client.get("/api/admin/users?q=admin&limit=1", headers=headers).json()[0]["role"] == "admin"
    assert client.get("/api/admin/plans?status=active", headers=headers).status_code == 200
    assert client.get("/api/admin/check-ins/pending?limit=1", headers=headers).status_code == 200
    assert client.get("/api/admin/disputes?status=pending", headers=headers).status_code == 200
    assert client.get("/api/admin/settlements?limit=1", headers=headers).status_code == 200
    assert client.get("/api/admin/transactions?limit=1", headers=headers).status_code == 200
    assert client.get("/api/admin/balances?limit=1", headers=headers).status_code == 200
    assert client.get("/api/admin/audit-logs?limit=1", headers=headers).status_code == 200


def test_admin_query_validation_and_missing_resources(admin_context):
    client = admin_context["client"]
    headers = admin_context["admin"]
    assert client.get("/api/admin/users?limit=0", headers=headers).status_code == 422
    assert client.get("/api/admin/plans?status=unknown", headers=headers).status_code == 422
    assert client.patch(
        "/api/admin/check-ins/missing/review",
        json={"review_status": "approved"},
        headers=headers,
    ).status_code == 404
    assert client.patch(
        "/api/admin/disputes/missing",
        json={"status": "resolved"},
        headers=headers,
    ).status_code == 404


def test_admin_page_csp_allows_its_same_origin_inline_assets(admin_context):
    response = admin_context["client"].get("/admin/")
    assert response.status_code == 200
    csp = response.headers["content-security-policy"]
    assert "script-src 'self' 'unsafe-inline'" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp


def test_admin_update_endpoints_require_admin_role(admin_context):
    client = admin_context["client"]
    response = client.patch(
        "/api/admin/disputes/missing",
        json={"status": "resolved"},
        headers=admin_context["member"],
    )
    assert response.status_code == 403


def test_admin_review_and_dispute_state_boundaries(admin_context):
    db = Session()
    plan_id = str(uuid.uuid4())
    settlement_id = str(uuid.uuid4())
    check_in_id = str(uuid.uuid4())
    dispute_id = str(uuid.uuid4())
    db.add(BettingPlan(
        id=plan_id,
        creator_id="admin-user",
        participant_id="member-user",
        status=PlanStatus.ACTIVE,
        bet_amount=10,
        start_date=datetime.utcnow() - timedelta(days=2),
        end_date=datetime.utcnow() + timedelta(days=2),
        creator_initial_weight=80,
        creator_target_weight=75,
        creator_target_weight_loss=5,
        participant_initial_weight=80,
        participant_target_weight=75,
        participant_target_weight_loss=5,
    ))
    db.add(CheckIn(
        id=check_in_id,
        user_id="member-user",
        plan_id=plan_id,
        weight=79,
        check_in_date=datetime.utcnow().date(),
        review_status=ReviewStatus.APPROVED,
    ))
    db.add(Settlement(
        id=settlement_id,
        plan_id=plan_id,
        creator_achieved=True,
        participant_achieved=False,
        creator_final_weight=75,
        participant_final_weight=80,
        creator_weight_loss=5,
        participant_weight_loss=0,
        creator_amount=20,
        participant_amount=0,
        platform_fee=0,
    ))
    db.add(Dispute(
        id=dispute_id,
        settlement_id=settlement_id,
        user_id="member-user",
        reason="测试争议",
        status=DisputeStatus.PENDING,
    ))
    db.commit()
    db.close()

    client = admin_context["client"]
    headers = admin_context["admin"]
    assert client.patch(
        f"/api/admin/check-ins/{check_in_id}/review",
        json={"review_status": "rejected"},
        headers=headers,
    ).status_code == 409
    assert client.patch(
        f"/api/admin/disputes/{dispute_id}",
        json={"status": "under_review"},
        headers=headers,
    ).status_code == 200
    assert client.patch(
        f"/api/admin/disputes/{dispute_id}",
        json={"status": "resolved", "admin_notes": "已核实"},
        headers=headers,
    ).status_code == 200
    assert client.patch(
        f"/api/admin/disputes/{dispute_id}",
        json={"status": "pending"},
        headers=headers,
    ).status_code == 409
