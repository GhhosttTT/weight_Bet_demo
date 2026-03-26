"""
结算二次确认选择匹配完整流程集成测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.database import Base, get_db
from app.models.settlement import Settlement


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """创建测试客户端"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def register_and_login(client, email, password="Test123456"):
    """注册并登录，返回 token 和用户 ID"""
    # 注册
    response = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "nickname": email.split("@")[0]
    })
    user_id = response.json()["user"]["id"]
    
    # 登录
    response = client.post("/api/auth/login", data={
        "email": email,
        "password": password
    })
    token = response.json()["access_token"]
    return user_id, token


def create_test_plan(client, creator_token, participant_email):
    """创建测试计划"""
    response = client.post("/api/betting-plans", json={
        "participant_email": participant_email,
        "bet_amount": 100.0,
        "start_date": (datetime.utcnow()).isoformat(),
        "end_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "description": "Integration test plan",
        "creator_initial_weight": 80.0,
        "creator_target_weight": 75.0,
        "creator_target_weight_loss": 5.0
    }, headers={"Authorization": f"Bearer {creator_token}"})
    return response.json()["id"]


def accept_plan(client, participant_token, plan_id):
    """参与者接受计划"""
    response = client.post(f"/api/betting-plans/{plan_id}/accept", json={
        "initial_weight": 75.0,
        "target_weight": 70.0,
        "target_weight_loss": 5.0
    }, headers={"Authorization": f"Bearer {participant_token}"})
    return response.status_code == 200


def confirm_plan(client, creator_token, plan_id):
    """创建者确认计划"""
    response = client.post(f"/api/betting-plans/{plan_id}/confirm", headers={
        "Authorization": f"Bearer {creator_token}"
    })
    return response.status_code == 200


class TestSettlementWorkflow:
    """结算完整工作流程测试"""
    
    def test_workflow_scenario_1_both_achieved(self, client):
        """场景 1：双方都达成目标（都选"都达成"）"""
        # 准备用户
        creator_id, creator_token = register_and_login(client, "creator1@test.com")
        participant_id, participant_token = register_and_login(client, "participant1@test.com")
        
        # 创建并接受计划
        plan_id = create_test_plan(client, creator_token, "participant1@test.com")
        accept_plan(client, participant_token, plan_id)
        confirm_plan(client, creator_token, plan_id)
        
        # 双方都选择"都达成"
        creator_choice = {"self_achieved": True, "opponent_achieved": True}
        participant_choice = {"self_achieved": True, "opponent_achieved": True}
        
        client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice, 
                   headers={"Authorization": f"Bearer {creator_token}"})
        client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice, 
                   headers={"Authorization": f"Bearer {participant_token}"})
        
        # 执行匹配
        match_response = client.post(f"/api/settlement-choices/{plan_id}/match",
                                    headers={"Authorization": f"Bearer {creator_token}"})
        
        assert match_response.status_code == 200
        result = match_response.json()
        assert result["matched"] is True
        assert result["both_achieved"] is True
        
        # 执行结算
        settlement_response = client.post(f"/api/settlements/execute/{plan_id}",
                                         headers={"Authorization": f"Bearer {creator_token}"})
        
        assert settlement_response.status_code == 200
        settlement = settlement_response.json()
        assert settlement["creator_achieved"] is True
        assert settlement["participant_achieved"] is True
        # 双方都应该拿回原赌金
        assert abs(settlement["creator_amount"] - 100.0) < 0.01
        assert abs(settlement["participant_amount"] - 100.0) < 0.01
        assert settlement["platform_fee"] == 0.0
    
    def test_workflow_scenario_2_creator_wins(self, client):
        """场景 2：创建者获胜（我成对方败 vs 我败对方成）"""
        creator_id, creator_token = register_and_login(client, "creator2@test.com")
        participant_id, participant_token = register_and_login(client, "participant2@test.com")
        
        plan_id = create_test_plan(client, creator_token, "participant2@test.com")
        accept_plan(client, participant_token, plan_id)
        confirm_plan(client, creator_token, plan_id)
        
        # 创建者选"我成对方败",参与者选"我败对方成"
        creator_choice = {"self_achieved": True, "opponent_achieved": False}
        participant_choice = {"self_achieved": False, "opponent_achieved": True}
        
        client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice,
                   headers={"Authorization": f"Bearer {creator_token}"})
        client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice,
                   headers={"Authorization": f"Bearer {participant_token}"})
        
        # 匹配
        match_response = client.post(f"/api/settlement-choices/{plan_id}/match",
                                    headers={"Authorization": f"Bearer {creator_token}"})
        
        assert match_response.json()["matched"] is True
        assert match_response.json()["creator_won"] is True
        
        # 结算
        settlement_response = client.post(f"/api/settlements/execute/{plan_id}",
                                         headers={"Authorization": f"Bearer {creator_token}"})
        
        settlement = settlement_response.json()
        # 创建者获得全部 200 元
        assert abs(settlement["creator_amount"] - 200.0) < 0.01
        assert settlement["participant_amount"] == 0.0
    
    def test_workflow_scenario_3_mismatch_round1_to_round2(self, client):
        """场景 3：第一轮不匹配，进入第二轮"""
        creator_id, creator_token = register_and_login(client, "creator3@test.com")
        participant_id, participant_token = register_and_login(client, "participant3@test.com")
        
        plan_id = create_test_plan(client, creator_token, "participant3@test.com")
        accept_plan(client, participant_token, plan_id)
        confirm_plan(client, creator_token, plan_id)
        
        # 第一轮：不匹配的选择
        creator_choice_r1 = {"self_achieved": True, "opponent_achieved": True}
        participant_choice_r1 = {"self_achieved": True, "opponent_achieved": False}
        
        client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice_r1,
                   headers={"Authorization": f"Bearer {creator_token}"})
        client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice_r1,
                   headers={"Authorization": f"Bearer {participant_token}"})
        
        # 第一轮匹配结果
        match_r1 = client.post(f"/api/settlement-choices/{plan_id}/match",
                              headers={"Authorization": f"Bearer {creator_token}"})
        
        assert match_r1.json()["matched"] is False
        assert match_r1.json()["go_to_next_round"] is True
        
        # 第二轮：提交新的选择（匹配）
        creator_choice_r2 = {"self_achieved": True, "opponent_achieved": False}
        participant_choice_r2 = {"self_achieved": False, "opponent_achieved": True}
        
        client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice_r2,
                   headers={"Authorization": f"Bearer {creator_token}"})
        client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice_r2,
                   headers={"Authorization": f"Bearer {participant_token}"})
        
        # 第二轮匹配
        match_r2 = client.post(f"/api/settlement-choices/{plan_id}/match",
                              headers={"Authorization": f"Bearer {creator_token}"})
        
        assert match_r2.json()["matched"] is True
        assert match_r2.json()["creator_won"] is True
    
    def test_workflow_scenario_4_arbitration(self, client):
        """场景 4：三次不匹配进入仲裁"""
        creator_id, creator_token = register_and_login(client, "creator4@test.com")
        participant_id, participant_token = register_and_login(client, "participant4@test.com")
        
        plan_id = create_test_plan(client, creator_token, "participant4@test.com")
        accept_plan(client, participant_token, plan_id)
        confirm_plan(client, creator_token, plan_id)
        
        # 模拟三轮都不匹配
        for round_num in range(1, 4):
            creator_choice = {"self_achieved": True, "opponent_achieved": True}
            participant_choice = {"self_achieved": True, "opponent_achieved": False}
            
            client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice,
                       headers={"Authorization": f"Bearer {creator_token}"})
            client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice,
                       headers={"Authorization": f"Bearer {participant_token}"})
            
            if round_num < 3:
                match_result = client.post(f"/api/settlement-choices/{plan_id}/match",
                                          headers={"Authorization": f"Bearer {creator_token}"})
                assert match_result.json()["go_to_next_round"] is True
        
        # 第三轮匹配应该进入仲裁
        match_r3 = client.post(f"/api/settlement-choices/{plan_id}/match",
                              headers={"Authorization": f"Bearer {creator_token}"})
        
        assert match_r3.json()["go_to_arbitration"] is True
        
        # 执行仲裁结算
        settlement_response = client.post(f"/api/settlements/execute/{plan_id}",
                                         headers={"Authorization": f"Bearer {creator_token}"})
        
        settlement = settlement_response.json()
        assert settlement["in_arbitration"] is True
        assert settlement["arbitration_fee"] > 0
        # 仲裁费应该是总赌金的 15%
        expected_fee = 200.0 * 0.15
        assert abs(settlement["arbitration_fee"] - expected_fee) < 0.01
    
    def test_workflow_scenario_5_both_failed(self, client):
        """场景 5：双方都未达成（都选"都未达成"）"""
        creator_id, creator_token = register_and_login(client, "creator5@test.com")
        participant_id, participant_token = register_and_login(client, "participant5@test.com")
        
        plan_id = create_test_plan(client, creator_token, "participant5@test.com")
        accept_plan(client, participant_token, plan_id)
        confirm_plan(client, creator_token, plan_id)
        
        # 双方都选择"都未达成"
        creator_choice = {"self_achieved": False, "opponent_achieved": False}
        participant_choice = {"self_achieved": False, "opponent_achieved": False}
        
        client.post(f"/api/settlement-choices/{plan_id}", json=creator_choice,
                   headers={"Authorization": f"Bearer {creator_token}"})
        client.post(f"/api/settlement-choices/{plan_id}", json=participant_choice,
                   headers={"Authorization": f"Bearer {participant_token}"})
        
        # 匹配
        match_response = client.post(f"/api/settlement-choices/{plan_id}/match",
                                    headers={"Authorization": f"Bearer {creator_token}"})
        
        assert match_response.json()["matched"] is True
        assert match_response.json()["both_failed"] is True
        
        # 结算
        settlement_response = client.post(f"/api/settlements/execute/{plan_id}",
                                         headers={"Authorization": f"Bearer {creator_token}"})
        
        settlement = settlement_response.json()
        # 扣除 10% 平台费后平分
        total = 200.0
        platform_fee = total * 0.10
        remaining = total - platform_fee
        each_share = remaining / 2
        
        assert abs(settlement["platform_fee"] - platform_fee) < 0.01
        assert abs(settlement["creator_amount"] - each_share) < 0.01
        assert abs(settlement["participant_amount"] - each_share) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
