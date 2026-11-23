"""资金与结算路由的 HTTP 权限矩阵测试。"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (
    Balance,
    BettingPlan,
    Gender,
    PlanStatus,
    Settlement,
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
)
from app.utils.security import create_access_token, hash_password


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
def financial_context():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_db

    db = Session()
    owner = User(
        id="finance-owner", email="owner@example.com", password_hash=hash_password("secret"),
        nickname="Owner", gender=Gender.OTHER, age=30, height=170, current_weight=70,
    )
    other = User(
        id="finance-other", email="other@example.com", password_hash=hash_password("secret"),
        nickname="Other", gender=Gender.OTHER, age=30, height=170, current_weight=70,
    )
    db.add_all([owner, other])
    db.add_all([
        Balance(user_id=owner.id, available_balance=100, frozen_balance=0),
        Balance(user_id=other.id, available_balance=100, frozen_balance=0),
    ])
    plan = BettingPlan(
        id="financial-plan",
        creator_id=owner.id,
        participant_id=other.id,
        status=PlanStatus.ACTIVE,
        bet_amount=20,
        start_date=datetime.utcnow() - timedelta(days=3),
        end_date=datetime.utcnow() - timedelta(days=1),
        creator_initial_weight=80,
        creator_target_weight=75,
        creator_target_weight_loss=5,
        participant_initial_weight=80,
        participant_target_weight=75,
        participant_target_weight_loss=5,
    )
    settlement = Settlement(
        id="financial-settlement",
        plan_id=plan.id,
        creator_achieved=True,
        participant_achieved=False,
        creator_final_weight=75,
        participant_final_weight=80,
        creator_weight_loss=5,
        participant_weight_loss=0,
        creator_amount=40,
        participant_amount=0,
        platform_fee=0,
    )
    transaction = Transaction(
        id="financial-transaction",
        user_id=owner.id,
        type=TransactionType.CHARGE,
        amount=20,
        status=TransactionStatus.COMPLETED,
    )
    db.add_all([plan, settlement, transaction])
    db.commit()
    db.close()

    client = TestClient(app)
    owner_id = "finance-owner"
    other_id = "finance-other"
    yield {
        "client": client,
        "owner": {"Authorization": f"Bearer {create_access_token({'sub': owner_id})}"},
        "other": {"Authorization": f"Bearer {create_access_token({'sub': other_id})}"},
    }

    client.close()
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


def test_balance_and_transactions_are_owner_scoped(financial_context):
    client = financial_context["client"]
    owner = financial_context["owner"]
    other = financial_context["other"]

    # FastAPI HTTPBearer 无凭据时返回 403；带非法/过期令牌时由认证中间件返回 401。
    assert client.get("/api/payments/users/finance-owner/balance").status_code == 403
    assert client.get("/api/payments/users/finance-owner/balance", headers=other).status_code == 403
    assert client.get("/api/payments/users/finance-owner/balance", headers=owner).status_code == 200
    assert client.get("/api/payments/users/finance-owner/transactions", headers=other).status_code == 403
    assert client.get("/api/payments/users/finance-owner/transactions", headers=owner).status_code == 200


def test_transaction_status_is_owner_scoped(financial_context):
    client = financial_context["client"]
    assert client.get(
        "/api/payments/transactions/financial-transaction",
        headers=financial_context["other"],
    ).status_code == 404
    assert client.get(
        "/api/payments/transactions/financial-transaction",
        headers=financial_context["owner"],
    ).status_code == 200
    assert client.get(
        "/api/payments/transactions/missing",
        headers=financial_context["owner"],
    ).status_code == 404


def test_settlement_reads_require_plan_participation(financial_context):
    client = financial_context["client"]
    owner = financial_context["owner"]
    other = financial_context["other"]

    assert client.get("/api/settlements/financial-settlement", headers=owner).status_code == 200
    assert client.get("/api/settlements/financial-settlement", headers=other).status_code == 200
    assert client.get("/api/settlements/financial-settlement", headers={"Authorization": "Bearer " + create_access_token({"sub": "missing-user"})}).status_code == 401
    assert client.get("/api/settlements/financial-settlement", headers={"Authorization": "Bearer " + create_access_token({"sub": "finance-owner"})}).status_code == 200
    assert client.get("/api/settlements/missing", headers=owner).status_code == 404


def test_settlement_calculation_and_dispute_require_participation(financial_context):
    client = financial_context["client"]
    owner = financial_context["owner"]
    other = financial_context["other"]
    dispute = {"reason": "结算金额需要人工复核", "description": "请复核结算记录"}

    assert client.get("/api/settlements/calculate/financial-plan", headers=owner).status_code == 200
    assert client.get("/api/settlements/calculate/financial-plan", headers=other).status_code == 200
    assert client.post("/api/settlements/financial-settlement/dispute", json=dispute, headers=other).status_code == 200
    assert client.post("/api/settlements/financial-settlement/dispute", json=dispute, headers=owner).status_code == 200
    owner_dispute = client.get("/api/settlements/financial-settlement/dispute", headers=owner)
    other_dispute = client.get("/api/settlements/financial-settlement/dispute", headers=other)
    assert owner_dispute.status_code == 200
    assert other_dispute.status_code == 200
    assert owner_dispute.json()["user_id"] == "finance-owner"
    assert other_dispute.json()["user_id"] == "finance-other"
    assert client.post("/api/settlements/financial-settlement/dispute", json=dispute, headers=owner).status_code == 400
