"""
结算选择 API 路由单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid
import json

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆盖 FastAPI 的数据库依赖
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """创建测试客户端"""
    # 多个接口测试模块都会修改 app.dependency_overrides；每个用例重新
    # 绑定本模块的数据库，避免收集顺序导致连接到已清理的测试库。
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    """创建测试用户并登录"""
    # 注册
    user_data = {
        "email": f"test_{uuid.uuid4()}@test.com",
        "password": "Test123456",
        "nickname": "TestUser",
        "gender": "male",
        "age": 30,
        "height": 175.0,
        "current_weight": 80.0,
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    # 登录获取 token
    login_data = {
        "email": user_data["email"],
        "password": "Test123456"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    user_id = response.json()["user_id"]
    db = TestingSessionLocal()
    db.query(User).filter(User.id == user_id).update({"payment_method_id": "test_pm_creator"})
    db.commit()
    db.close()
    return {"user_id": user_id, "token": token}


@pytest.fixture
def test_plan_with_participant(client, test_user):
    """创建有参与者的测试计划"""
    creator_token = test_user["token"]
    creator_id = test_user["user_id"]
    
    # 创建第二个用户（参与者）
    participant_data = {
        "email": f"participant_{uuid.uuid4()}@test.com",
        "password": "Test123456",
        "nickname": "Participant",
        "gender": "female",
        "age": 28,
        "height": 165.0,
        "current_weight": 75.0,
    }
    response = client.post("/api/auth/register", json=participant_data)
    participant_id = response.json()["user_id"]
    
    # 创建计划
    plan_data = {
        "participant_email": participant_data["email"],
        "bet_amount": 100.0,
        "start_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "end_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),  # 已到期
        "description": "Test plan",
        "initial_weight": 80.0,
        "target_weight": 75.0,
        "creator_initial_weight": 80.0,
        "creator_target_weight": 75.0,
        "creator_target_weight_loss": 5.0
    }
    headers = {"Authorization": f"Bearer {creator_token}"}
    charge_response = client.post(
        "/api/payments/charge",
        json={"amount": 200.0, "payment_method_id": "test_pm_creator"},
        headers=headers,
    )
    assert charge_response.status_code == 200
    response = client.post("/api/betting-plans", json=plan_data, headers=headers)
    plan_id = response.json()["id"]
    
    # 参与者接受计划
    login_data = {
        "email": participant_data["email"],
        "password": "Test123456"
    }
    response = client.post("/api/auth/login", json=login_data)
    participant_token = response.json()["access_token"]
    db = TestingSessionLocal()
    db.query(User).filter(User.id == participant_id).update({"payment_method_id": "test_pm_participant"})
    db.commit()
    db.close()

    participant_headers = {"Authorization": f"Bearer {participant_token}"}
    charge_response = client.post(
        "/api/payments/charge",
        json={"amount": 200.0, "payment_method_id": "test_pm_participant"},
        headers=participant_headers,
    )
    assert charge_response.status_code == 200
    
    accept_data = {
        "initial_weight": 75.0,
        "target_weight": 70.0,
        "target_weight_loss": 5.0
    }
    response = client.post(
        f"/api/betting-plans/{plan_id}/accept",
        json=accept_data,
        headers=participant_headers,
    )
    
    # 创建者确认
    headers = {"Authorization": f"Bearer {creator_token}"}
    response = client.post(f"/api/betting-plans/{plan_id}/confirm", headers=headers)
    
    return {
        "plan_id": plan_id,
        "creator_id": creator_id,
        "creator_token": creator_token,
        "participant_id": participant_id,
        "participant_token": participant_token
    }


class TestSettlementChoiceAPI:
    """结算选择 API 测试类"""

    def test_abandon_requires_explicit_confirmation(self, client, test_plan_with_participant):
        plan = test_plan_with_participant
        response = client.post(
            f"/api/betting-plans/{plan['plan_id']}/abandon",
            json={"confirmation": False},
            headers={"Authorization": f"Bearer {plan['creator_token']}"},
        )

        assert response.status_code == 400
        assert response.json()["message"] == "必须确认放弃计划后才能继续"

        db = TestingSessionLocal()
        try:
            stored_plan = db.query(BettingPlan).filter(
                BettingPlan.id == plan["plan_id"]
            ).first()
            assert stored_plan.status == PlanStatus.ACTIVE
        finally:
            db.close()

    def test_payment_endpoints_require_bound_payment_method(self, client, test_user):
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        missing_method = client.post(
            "/api/payments/charge",
            json={"amount": 10.0},
            headers=headers,
        )
        assert missing_method.status_code == 422

        wrong_method = client.post(
            "/api/payments/charge",
            json={"amount": 10.0, "payment_method_id": "other_user_pm"},
            headers=headers,
        )
        assert wrong_method.status_code == 400
        assert wrong_method.json()["message"] == "支付方式未绑定或已失效"

        wrong_withdraw_method = client.post(
            "/api/payments/withdraw",
            json={"amount": 10.0, "payment_method_id": "other_user_pm"},
            headers=headers,
        )
        assert wrong_withdraw_method.status_code == 400

    def test_plan_details_requires_authentication(self, client, test_plan_with_participant):
        """计划详情不能匿名读取"""
        plan_id = test_plan_with_participant["plan_id"]
        response = client.get(f"/api/betting-plans/{plan_id}")
        assert response.status_code == 403

    def test_plan_details_allows_participant(self, client, test_plan_with_participant):
        """计划参与者可以读取详情"""
        plan_id = test_plan_with_participant["plan_id"]
        token = test_plan_with_participant["participant_token"]
        response = client.get(
            f"/api/betting-plans/{plan_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == plan_id
    
    def test_submit_choice_success(self, client, test_plan_with_participant):
        """测试提交选择成功"""
        plan_id = test_plan_with_participant["plan_id"]
        creator_token = test_plan_with_participant["creator_token"]
        
        choice_data = {
            "self_achieved": True,
            "opponent_achieved": False
        }
        headers = {"Authorization": f"Bearer {creator_token}"}
        response = client.post(
            f"/api/settlement-choices/{plan_id}",
            json=choice_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == plan_id
        assert data["self_achieved"] is True
        assert data["opponent_achieved"] is False
        assert data["round"] == 1
    
    def test_submit_choice_unauthorized(self, client, test_plan_with_participant):
        """测试未授权用户提交选择"""
        plan_id = test_plan_with_participant["plan_id"]
        
        # 创建第三个用户（不是计划参与者）
        outsider_data = {
            "email": f"outsider_{uuid.uuid4()}@test.com",
            "password": "Test123456",
            "nickname": "Outsider",
            "gender": "other",
            "age": 30,
            "height": 175.0,
            "current_weight": 80.0,
        }
        response = client.post("/api/auth/register", json=outsider_data)
        login_data = {
            "email": outsider_data["email"],
            "password": "Test123456"
        }
        response = client.post("/api/auth/login", json=login_data)
        outsider_token = response.json()["access_token"]
        
        choice_data = {
            "self_achieved": True,
            "opponent_achieved": False
        }
        headers = {"Authorization": f"Bearer {outsider_token}"}
        response = client.post(
            f"/api/settlement-choices/{plan_id}",
            json=choice_data,
            headers=headers
        )
        
        assert response.status_code == 403
        assert "您不是该计划的参与者" in response.json()["message"]
    
    def test_submit_choice_invalid_data(self, client, test_plan_with_participant):
        """测试无效数据"""
        plan_id = test_plan_with_participant["plan_id"]
        creator_token = test_plan_with_participant["creator_token"]
        
        # 缺少必需字段
        choice_data = {
            "self_achieved": True
            # 缺少 opponent_achieved
        }
        headers = {"Authorization": f"Bearer {creator_token}"}
        response = client.post(
            f"/api/settlement-choices/{plan_id}",
            json=choice_data,
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_selection_status(self, client, test_plan_with_participant):
        """测试获取选择状态"""
        plan_id = test_plan_with_participant["plan_id"]
        creator_token = test_plan_with_participant["creator_token"]
        
        # 先提交一个选择
        choice_data = {
            "self_achieved": True,
            "opponent_achieved": False
        }
        headers = {"Authorization": f"Bearer {creator_token}"}
        client.post(f"/api/settlement-choices/{plan_id}", json=choice_data, headers=headers)
        
        # 获取状态
        response = client.get(
            f"/api/settlement-choices/{plan_id}/status",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == plan_id
        assert data["current_round"] == 1
        assert data["creator_submitted"] is True
        assert data["participant_submitted"] is False
        assert data["current_user_submitted"] is True
        assert data["creator_choice"] is not None
    
    def test_match_choices(self, client, test_plan_with_participant):
        """测试匹配选择"""
        plan_id = test_plan_with_participant["plan_id"]
        creator_token = test_plan_with_participant["creator_token"]
        participant_token = test_plan_with_participant["participant_token"]
        
        # 双方都提交匹配的选择
        creator_choice = {
            "self_achieved": True,
            "opponent_achieved": False
        }
        participant_choice = {
            "self_achieved": False,
            "opponent_achieved": True
        }
        
        headers_creator = {"Authorization": f"Bearer {creator_token}"}
        headers_participant = {"Authorization": f"Bearer {participant_token}"}
        
        client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice, headers=headers_creator)
        client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice, headers=headers_participant)
        
        # 执行匹配
        response = client.post(
            f"/api/settlement-choices/{plan_id}/match",
            headers=headers_creator
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["matched"] is True
        assert data["creator_won"] is True
        assert data["go_to_next_round"] is False
        assert data["go_to_arbitration"] is False
    
    def test_check_timeout(self, client, test_plan_with_participant):
        """测试超时检查"""
        plan_id = test_plan_with_participant["plan_id"]
        creator_token = test_plan_with_participant["creator_token"]
        
        # 只有一方提交
        choice_data = {
            "self_achieved": True,
            "opponent_achieved": False
        }
        headers = {"Authorization": f"Bearer {creator_token}"}
        client.post(f"/api/settlement-choices/{plan_id}", json=choice_data, headers=headers)
        
        # 检查超时（应该未达到 24 小时）
        response = client.get(
            f"/api/settlement-choices/{plan_id}/check-timeout?timeout_hours=24",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "等待对方提交" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
