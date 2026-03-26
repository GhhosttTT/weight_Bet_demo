"""
结算选择服务单元测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.database import Base, get_db
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.settlement_choice import SettlementChoice
from app.services.settlement_choice_service import SettlementChoiceService
from app.schemas.settlement_choice import SettlementChoiceRequest


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_settlement_choice.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
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
    return user1, user2


@pytest.fixture
def test_plan(db_session, test_users):
    """创建测试计划"""
    creator, participant = test_users
    plan = BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=creator.id,
        participant_id=participant.id,
        bet_amount=100.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() - timedelta(days=1),  # 已到期
        creator_initial_weight=80.0,
        creator_target_weight=75.0,
        creator_target_weight_loss=5.0,
        participant_initial_weight=75.0,
        participant_target_weight=70.0,
        participant_target_weight_loss=5.0,
        status=PlanStatus.ACTIVE
    )
    db_session.add(plan)
    db_session.commit()
    return plan


class TestSubmitChoice:
    """测试提交结算选择"""
    
    def test_submit_choice_success(self, db_session, test_plan, test_users):
        """测试成功提交选择"""
        creator, _ = test_users
        request = SettlementChoiceRequest(
            self_achieved=True,
            opponent_achieved=False
        )
        
        result = SettlementChoiceService.submit_choice(
            db_session, test_plan.id, creator.id, request
        )
        
        assert result.plan_id == test_plan.id
        assert result.user_id == creator.id
        assert result.self_achieved is True
        assert result.opponent_achieved is False
        assert result.round == 1
    
    def test_submit_choice_non_existent_plan(self, db_session, test_users):
        """测试不存在的计划"""
        creator, _ = test_users
        request = SettlementChoiceRequest(
            self_achieved=True,
            opponent_achieved=False
        )
        
        with pytest.raises(Exception) as exc_info:
            SettlementChoiceService.submit_choice(
                db_session, "non-existent-id", creator.id, request
            )
        assert "计划不存在" in str(exc_info.value)
    
    def test_submit_choice_unauthorized_user(self, db_session, test_plan, test_users):
        """测试未授权用户"""
        _, participant = test_users
        unauthorized_user_id = str(uuid.uuid4())
        request = SettlementChoiceRequest(
            self_achieved=True,
            opponent_achieved=False
        )
        
        with pytest.raises(Exception) as exc_info:
            SettlementChoiceService.submit_choice(
                db_session, test_plan.id, unauthorized_user_id, request
            )
        assert "您不是该计划的参与者" in str(exc_info.value)
    
    def test_submit_choice_completed_plan(self, db_session, test_plan, test_users):
        """测试已完成计划"""
        creator, _ = test_users
        test_plan.status = PlanStatus.COMPLETED
        db_session.commit()
        
        request = SettlementChoiceRequest(
            self_achieved=True,
            opponent_achieved=False
        )
        
        with pytest.raises(Exception) as exc_info:
            SettlementChoiceService.submit_choice(
                db_session, test_plan.id, creator.id, request
            )
        assert "计划已结算" in str(exc_info.value)
    
    def test_submit_choice_duplicate(self, db_session, test_plan, test_users):
        """测试重复提交"""
        creator, _ = test_users
        request = SettlementChoiceRequest(
            self_achieved=True,
            opponent_achieved=False
        )
        
        # 第一次提交
        SettlementChoiceService.submit_choice(
            db_session, test_plan.id, creator.id, request
        )
        
        # 第二次提交应该失败
        with pytest.raises(Exception) as exc_info:
            SettlementChoiceService.submit_choice(
                db_session, test_plan.id, creator.id, request
            )
        assert "您已在第" in str(exc_info.value)


class TestMatchChoices:
    """测试选择匹配逻辑"""
    
    def test_match_both_achieved(self, db_session, test_plan, test_users):
        """测试双方都达成"""
        creator, participant = test_users
        
        # 双方都选择"都达成"
        req1 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=True)
        req2 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=True)
        
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req1)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, participant.id, req2)
        
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
        
        assert result.matched is True
        assert result.both_achieved is True
        assert result.creator_won is None
        assert "双方都达成" in result.message
    
    def test_match_both_failed(self, db_session, test_plan, test_users):
        """测试双方都未达成"""
        creator, participant = test_users
        
        # 双方都选择"都未达成"
        req1 = SettlementChoiceRequest(self_achieved=False, opponent_achieved=False)
        req2 = SettlementChoiceRequest(self_achieved=False, opponent_achieved=False)
        
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req1)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, participant.id, req2)
        
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
        
        assert result.matched is True
        assert result.both_failed is True
        assert result.both_achieved is False
        assert "双方都未达成" in result.message
    
    def test_match_creator_wins(self, db_session, test_plan, test_users):
        """测试创建者获胜"""
        creator, participant = test_users
        
        # 创建者选"我成对方败",参与者选"我败对方成"
        req1 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        req2 = SettlementChoiceRequest(self_achieved=False, opponent_achieved=True)
        
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req1)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, participant.id, req2)
        
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
        
        assert result.matched is True
        assert result.creator_won is True
        assert "创建者获胜" in result.message
    
    def test_match_participant_wins(self, db_session, test_plan, test_users):
        """测试参与者获胜"""
        creator, participant = test_users
        
        # 创建者选"我败对方成",参与者选"我成对方败"
        req1 = SettlementChoiceRequest(self_achieved=False, opponent_achieved=True)
        req2 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req1)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, participant.id, req2)
        
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
        
        assert result.matched is True
        assert result.creator_won is False
        assert "参与者获胜" in result.message
    
    def test_match_no_match_round1(self, db_session, test_plan, test_users):
        """测试选择不匹配（第 1 轮）"""
        creator, participant = test_users
        
        # 双方都选"我达成，对方达成"和"我达成，对方未达成"（不匹配）
        req1 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=True)
        req2 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req1)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, participant.id, req2)
        
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
        
        assert result.matched is False
        assert result.go_to_next_round is True
        assert result.go_to_arbitration is False
    
    def test_match_go_to_arbitration_round3(self, db_session, test_plan, test_users):
        """测试三次不匹配进入仲裁"""
        creator, participant = test_users
            
        # 模拟三轮都不匹配
        for round_num in range(1, 4):
            req1 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=True)
            req2 = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
                
            choice1 = SettlementChoice(
                id=str(uuid.uuid4()),
                plan_id=test_plan.id,
                user_id=creator.id,
                self_achieved=req1.self_achieved,
                opponent_achieved=req1.opponent_achieved,
                round=round_num
            )
            choice2 = SettlementChoice(
                id=str(uuid.uuid4()),
                plan_id=test_plan.id,
                user_id=participant.id,
                self_achieved=req2.self_achieved,
                opponent_achieved=req2.opponent_achieved,
                round=round_num
            )
            db_session.add(choice1)
            db_session.add(choice2)
            db_session.commit()
            
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
            
        assert result.matched is False
        assert result.go_to_arbitration is True
        assert "三次选择不匹配" in result.message
    
    def test_match_incomplete_submissions(self, db_session, test_plan, test_users):
        """测试只有一方提交"""
        creator, _ = test_users
        
        req = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req)
        
        result = SettlementChoiceService.match_choices(db_session, test_plan.id)
        
        assert result.matched is False
        assert "等待双方提交" in result.message


class TestGetSelectionStatus:
    """测试获取选择状态"""
    
    def test_get_status_no_submissions(self, db_session, test_plan, test_users):
        """测试没有提交时的状态"""
        creator, _ = test_users
        
        status = SettlementChoiceService.get_selection_status(
            db_session, test_plan.id, creator.id
        )
        
        assert status.current_round == 1
        assert status.creator_submitted is False
        assert status.participant_submitted is False
        assert status.settlement_completed is False
    
    def test_get_status_one_submitted(self, db_session, test_plan, test_users):
        """测试一方已提交"""
        creator, _ = test_users
        req = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req)
        
        status = SettlementChoiceService.get_selection_status(
            db_session, test_plan.id, creator.id
        )
        
        assert status.current_round == 1
        assert status.creator_submitted is True
        assert status.participant_submitted is False
        assert status.creator_choice is not None


class TestCheckTimeoutAndAdvance:
    """测试超时检查和推进"""
    
    def test_timeout_not_reached(self, db_session, test_plan, test_users):
        """测试未达到超时"""
        creator, _ = test_users
        req = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req)
        
        success, message = SettlementChoiceService.check_timeout_and_advance(
            db_session, test_plan.id, timeout_hours=24
        )
        
        assert success is False
        assert "等待对方提交" in message
    
    def test_timeout_reached_advance_round(self, db_session, test_plan, test_users):
        """测试超时并推进到下一轮"""
        creator, _ = test_users
        
        # 创建一个超时的选择（25 小时前）
        choice = SettlementChoice(
            id=str(uuid.uuid4()),
            plan_id=test_plan.id,
            user_id=creator.id,
            self_achieved=True,
            opponent_achieved=False,
            round=1,
            created_at=datetime.utcnow() - timedelta(hours=25)
        )
        db_session.add(choice)
        db_session.commit()
        
        success, message = SettlementChoiceService.check_timeout_and_advance(
            db_session, test_plan.id, timeout_hours=24
        )
        
        assert success is True
        assert "round 2" in message.lower()
    
    def test_timeout_both_submitted(self, db_session, test_plan, test_users):
        """测试双方都已提交"""
        creator, participant = test_users
        
        req = SettlementChoiceRequest(self_achieved=True, opponent_achieved=False)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, creator.id, req)
        SettlementChoiceService.submit_choice(db_session, test_plan.id, participant.id, req)
        
        success, message = SettlementChoiceService.check_timeout_and_advance(
            db_session, test_plan.id, timeout_hours=24
        )
        
        assert success is False
        assert "双方均已提交" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
