"""
仲裁服务单元测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.database import Base
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.check_in import CheckIn
from app.services.arbitration_service import ArbitrationService


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_arbitration.db"
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


class TestArbitrationService:
    """仲裁服务测试类"""
    
    def test_arbitration_creator_achieved_participant_failed(self, db_session, test_plan, test_users):
        """测试仲裁：创建者达成，参与者未达成"""
        creator, participant = test_users
        
        # 添加打卡记录
        check_in_creator = CheckIn(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            plan_id=test_plan.id,
            weight=74.0,  # 减重 6kg，达成目标
            check_in_date=datetime.utcnow().date()
        )
        check_in_participant = CheckIn(
            id=str(uuid.uuid4()),
            user_id=participant.id,
            plan_id=test_plan.id,
            weight=73.0,  # 减重 2kg，未达成目标
            check_in_date=datetime.utcnow().date()
        )
        db_session.add(check_in_creator)
        db_session.add(check_in_participant)
        db_session.commit()
        
        result = ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        assert result.plan_id == test_plan.id
        assert result.creator_achieved is True
        assert result.participant_achieved is False
        assert result.in_arbitration is True
        assert result.arbitration_fee > 0
        # 创建者应该获得剩余金额（85%）
        expected_amount = (test_plan.bet_amount * 2) * 0.85
        assert abs(result.creator_amount - expected_amount) < 0.01
        assert result.participant_amount == 0.0
    
    def test_arbitration_participant_achieved_creator_failed(self, db_session, test_plan, test_users):
        """测试仲裁：参与者达成，创建者未达成"""
        creator, participant = test_users
        
        # 添加打卡记录
        check_in_creator = CheckIn(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            plan_id=test_plan.id,
            weight=78.0,  # 减重 2kg，未达成目标
            check_in_date=datetime.utcnow().date()
        )
        check_in_participant = CheckIn(
            id=str(uuid.uuid4()),
            user_id=participant.id,
            plan_id=test_plan.id,
            weight=69.0,  # 减重 6kg，达成目标
            check_in_date=datetime.utcnow().date()
        )
        db_session.add(check_in_creator)
        db_session.add(check_in_participant)
        db_session.commit()
        
        result = ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        assert result.plan_id == test_plan.id
        assert result.creator_achieved is False
        assert result.participant_achieved is True
        assert result.in_arbitration is True
        # 参与者应该获得剩余金额（85%）
        expected_amount = (test_plan.bet_amount * 2) * 0.85
        assert abs(result.participant_amount - expected_amount) < 0.01
        assert result.creator_amount == 0.0
    
    def test_arbitration_both_achieved(self, db_session, test_plan, test_users):
        """测试仲裁：双方都达成"""
        creator, participant = test_users
        
        # 添加打卡记录
        check_in_creator = CheckIn(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            plan_id=test_plan.id,
            weight=74.0,  # 减重 6kg，达成目标
            check_in_date=datetime.utcnow().date()
        )
        check_in_participant = CheckIn(
            id=str(uuid.uuid4()),
            user_id=participant.id,
            plan_id=test_plan.id,
            weight=69.0,  # 减重 6kg，达成目标
            check_in_date=datetime.utcnow().date()
        )
        db_session.add(check_in_creator)
        db_session.add(check_in_participant)
        db_session.commit()
        
        result = ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        assert result.plan_id == test_plan.id
        assert result.creator_achieved is True
        assert result.participant_achieved is True
        assert result.in_arbitration is True
        # 双方平分剩余金额（各 42.5%）
        expected_each = (test_plan.bet_amount * 2) * 0.85 / 2
        assert abs(result.creator_amount - expected_each) < 0.01
        assert abs(result.participant_amount - expected_each) < 0.01
    
    def test_arbitration_both_failed(self, db_session, test_plan, test_users):
        """测试仲裁：双方都未达成"""
        creator, participant = test_users
        
        # 添加打卡记录
        check_in_creator = CheckIn(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            plan_id=test_plan.id,
            weight=78.0,  # 减重 2kg，未达成目标
            check_in_date=datetime.utcnow().date()
        )
        check_in_participant = CheckIn(
            id=str(uuid.uuid4()),
            user_id=participant.id,
            plan_id=test_plan.id,
            weight=73.0,  # 减重 2kg，未达成目标
            check_in_date=datetime.utcnow().date()
        )
        db_session.add(check_in_creator)
        db_session.add(check_in_participant)
        db_session.commit()
        
        result = ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        assert result.plan_id == test_plan.id
        assert result.creator_achieved is False
        assert result.participant_achieved is False
        assert result.in_arbitration is True
        # 双方平分剩余金额（各 42.5%）
        expected_each = (test_plan.bet_amount * 2) * 0.85 / 2
        assert abs(result.creator_amount - expected_each) < 0.01
        assert abs(result.participant_amount - expected_each) < 0.01
    
    def test_arbitration_no_checkin_data(self, db_session, test_plan, test_users):
        """测试仲裁：没有打卡数据"""
        creator, participant = test_users
        
        # 不添加打卡记录，使用初始体重
        result = ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        assert result.plan_id == test_plan.id
        assert result.in_arbitration is True
        assert result.arbitration_fee > 0
        # 双方都未达成，平分剩余金额
        expected_each = (test_plan.bet_amount * 2) * 0.85 / 2
        assert abs(result.creator_amount - expected_each) < 0.01
        assert abs(result.participant_amount - expected_each) < 0.01
    
    def test_arbitration_non_existent_plan(self, db_session, test_users):
        """测试不存在的计划"""
        creator, _ = test_users
        
        with pytest.raises(Exception) as exc_info:
            ArbitrationService.start_arbitration(db_session, "non-existent-id")
        assert "计划不存在" in str(exc_info.value)
    
    def test_arbitration_already_completed(self, db_session, test_plan, test_users):
        """测试已完成计划"""
        creator, _ = test_users
        test_plan.status = PlanStatus.COMPLETED
        db_session.commit()
        
        with pytest.raises(Exception) as exc_info:
            ArbitrationService.start_arbitration(db_session, test_plan.id)
        assert "计划已结算" in str(exc_info.value)
    
    def test_arbitration_updates_plan_status(self, db_session, test_plan, test_users):
        """测试仲裁后计划状态更新"""
        creator, participant = test_users
        
        # 添加打卡记录
        check_in = CheckIn(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            plan_id=test_plan.id,
            weight=74.0,
            check_in_date=datetime.utcnow().date()
        )
        db_session.add(check_in)
        db_session.commit()
        
        assert test_plan.status == PlanStatus.ACTIVE
        
        ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        assert test_plan.status == PlanStatus.COMPLETED
    
    def test_arbitration_fee_calculation(self, db_session, test_plan, test_users):
        """测试仲裁费用计算"""
        creator, _ = test_users
        
        # 添加打卡记录
        check_in = CheckIn(
            id=str(uuid.uuid4()),
            user_id=creator.id,
            plan_id=test_plan.id,
            weight=74.0,
            check_in_date=datetime.utcnow().date()
        )
        db_session.add(check_in)
        db_session.commit()
        
        result = ArbitrationService.start_arbitration(db_session, test_plan.id)
        
        # 仲裁费应该是总赌金的 15%
        expected_fee = (test_plan.bet_amount * 2) * 0.15
        assert abs(result.arbitration_fee - expected_fee) < 0.01
        # 验证总金额守恒
        total_distributed = result.creator_amount + result.participant_amount + result.arbitration_fee
        assert abs(total_distributed - (test_plan.bet_amount * 2)) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
