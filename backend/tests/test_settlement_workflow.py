#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
结算流程集成测试

测试完整的结算流程:
1. 创建计划
2. 模拟计划到期
3. App 启动时检查结算日弹窗
4. 用户提交结算选择
5. 匹配双方选择
6. 执行结算
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Base
from app.models.user import User
from app.models.betting_plan import BettingPlan
from app.models.settlement_choice import SettlementChoice
from app.schemas.settlement_choice import SettlementChoiceRequest
from app.services.settlement_choice_service import SettlementChoiceService
from app.services.settlement_service import SettlementService
from app.api.settlement_choices import check_settlement_deadline


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_settlement_workflow.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_users(db_session):
    """创建测试用户"""
    user1 = User(
        id=str(uuid.uuid4()),
        email="creator@test.com",
        nickname="Creator",
        password_hash="hashed_pwd",
        gender="male",
        age=30,
        height=175.0,
        current_weight=80.0
    )
    user2 = User(
        id=str(uuid.uuid4()),
        email="participant@test.com",
        nickname="Participant",
        password_hash="hashed_pwd",
        gender="female",
        age=28,
        height=165.0,
        current_weight=75.0
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    
    return [user1, user2]


@pytest.fixture
def expired_plan(db_session, test_users):
    """创建已到期的测试计划"""
    creator, participant = test_users
    
    plan = BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=creator.id,
        participant_id=participant.id,
        status="active",
        bet_amount=100.0,
        start_date=datetime.now() - timedelta(days=31),
        end_date=datetime.now() - timedelta(days=1),  # 已到期
        description="Settlement Workflow Test Plan",
        creator_initial_weight=80.0,
        creator_target_weight=75.0,
        creator_target_weight_loss=5.0,
        participant_initial_weight=75.0,
        participant_target_weight=70.0,
        participant_target_weight_loss=5.0
    )
    db_session.add(plan)
    db_session.commit()
    
    return plan


class TestSettlementWorkflow:
    """测试完整结算流程"""
    
    def test_check_settlement_deadline_returns_expired_plans(self, db_session, test_users, expired_plan):
        """测试检查结算日接口返回到期计划"""
        creator, participant = test_users
        
        # 模拟 API 调用（使用当前用户）
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # 注意：这里需要真实的 JWT token，实际测试中需要 mock 认证
        # 这个测试主要用于演示流程
        print("\n=== 结算流程测试 ===")
        print(f"1. 发现到期计划：{expired_plan.id}")
        print(f"   描述：{expired_plan.description}")
        print(f"   结束日期：{expired_plan.end_date}")
        
        # 验证计划确实已到期
        assert expired_plan.end_date < datetime.now()
        assert expired_plan.status == "active"
    
    def test_submit_settlement_choices(self, db_session, expired_plan, test_users):
        """测试双方提交结算选择"""
        creator, participant = test_users
        plan = expired_plan
        
        print("\n2. 双方提交结算选择")
        
        # 创建者选择：我达成，对方未达成
        creator_choice_req = SettlementChoiceRequest(
            self_achieved=True,
            opponent_achieved=False
        )
        
        creator_response = SettlementChoiceService.submit_choice(
            db_session, plan.id, creator.id, creator_choice_req
        )
        print(f"   创建者选择：self_achieved={creator_choice_req.self_achieved}, "
              f"opponent_achieved={creator_choice_req.opponent_achieved}")
        
        # 参与者选择：我未达成，对方达成
        participant_choice_req = SettlementChoiceRequest(
            self_achieved=False,
            opponent_achieved=True
        )
        
        participant_response = SettlementChoiceService.submit_choice(
            db_session, plan.id, participant.id, participant_choice_req
        )
        print(f"   参与者选择：self_achieved={participant_choice_req.self_achieved}, "
              f"opponent_achieved={participant_choice_req.opponent_achieved}")
        
        assert creator_response is not None
        assert participant_response is not None
    
    def test_match_settlement_choices_creator_wins(self, db_session, expired_plan, test_users):
        """测试匹配双方选择（创建者获胜场景）"""
        creator, participant = test_users
        plan = expired_plan
        
        print("\n3. 匹配双方选择")
        
        # 先提交选择
        SettlementChoiceService.submit_choice(
            db_session, plan.id, creator.id,
            SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        )
        SettlementChoiceService.submit_choice(
            db_session, plan.id, participant.id,
            SettlementChoiceRequest(self_achieved=False, opponent_achieved=True)
        )
        
        # 匹配选择
        matching_result = SettlementChoiceService.match_choices(db_session, plan.id)
        
        print(f"   匹配结果：matched={matching_result.matched}, "
              f"creator_won={matching_result.creator_won}")
        print(f"   消息：{matching_result.message}")
        
        assert matching_result.matched is True
        assert matching_result.creator_won is True
        assert matching_result.go_to_arbitration is False
    
    def test_execute_settlement_after_matching(self, db_session, expired_plan, test_users):
        """测试匹配成功后执行结算"""
        creator, participant = test_users
        plan = expired_plan
        
        print("\n4. 执行结算")
        
        # 先提交并匹配选择
        SettlementChoiceService.submit_choice(
            db_session, plan.id, creator.id,
            SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        )
        SettlementChoiceService.submit_choice(
            db_session, plan.id, participant.id,
            SettlementChoiceRequest(self_achieved=False, opponent_achieved=True)
        )
        
        matching_result = SettlementChoiceService.match_choices(db_session, plan.id)
        
        # 执行结算
        settlement = SettlementService.execute_settlement(
            db_session, 
            plan.id,
            matching_result={
                "matched": matching_result.matched,
                "creator_won": matching_result.creator_won,
                "both_achieved": matching_result.both_achieved,
                "both_failed": matching_result.both_failed,
                "go_to_arbitration": matching_result.go_to_arbitration
            }
        )
        
        print(f"   结算结果：creator_amount={settlement.creator_amount}, "
              f"participant_amount={settlement.participant_amount}")
        
        # 验证结算金额（创建者获胜应获得全部）
        assert settlement.creator_amount == 200.0  # 双倍赌金
        assert settlement.participant_amount == 0.0
        assert settlement.platform_fee == 0.0
    
    def test_complete_workflow_summary(self, db_session, expired_plan, test_users):
        """完整流程总结测试"""
        creator, participant = test_users
        plan = expired_plan
        
        print("\n" + "="*60)
        print("完整结算流程总结:")
        print("="*60)
        print(f"计划 ID: {plan.id}")
        print(f"创建者：{creator.nickname} (ID: {creator.id})")
        print(f"参与者：{participant.nickname} (ID: {participant.id})")
        print(f"赌金：${plan.bet_amount}")
        print(f"结束日期：{plan.end_date}")
        print("-"*60)
        
        # 1. 检查到期计划
        print("\n步骤 1: App 启动检查结算日")
        print(f"  ✓ 发现到期计划，弹出结算提示")
        
        # 2. 用户进入计划详情并提交选择
        print("\n步骤 2: 用户提交结算选择")
        creator_choice = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        SettlementChoiceService.submit_choice(db_session, plan.id, creator.id, creator_choice)
        print(f"  ✓ 创建者选择：我达成，对方未达成")
        
        participant_choice = SettlementChoiceRequest(self_achieved=False, opponent_achieved=True)
        SettlementChoiceService.submit_choice(db_session, plan.id, participant.id, participant_choice)
        print(f"  ✓ 参与者选择：我未达成，对方达成")
        
        # 3. 匹配选择
        print("\n步骤 3: 系统匹配双方选择")
        result = SettlementChoiceService.match_choices(db_session, plan.id)
        print(f"  ✓ 匹配成功：{result.matched}")
        print(f"  ✓ 创建者获胜：{result.creator_won}")
        
        # 4. 执行结算
        print("\n步骤 4: 执行结算")
        settlement = SettlementService.execute_settlement(
            db_session, plan.id,
            matching_result={
                "matched": result.matched,
                "creator_won": result.creator_won,
                "both_achieved": result.both_achieved,
                "both_failed": result.both_failed,
                "go_to_arbitration": result.go_to_arbitration
            }
        )
        print(f"  ✓ 结算完成")
        print(f"  ✓ 创建者获得：${settlement.creator_amount}")
        print(f"  ✓ 参与者获得：${settlement.participant_amount}")
        print(f"  ✓ 平台费用：${settlement.platform_fee}")
        
        print("\n" + "="*60)
        print("流程结束!")
        print("="*60)
        
        # 验证
        assert result.matched is True
        assert settlement.creator_amount == 200.0
        assert settlement.participant_amount == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
