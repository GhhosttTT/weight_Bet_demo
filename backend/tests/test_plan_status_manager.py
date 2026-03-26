"""
测试计划状态管理器
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.user import User
from app.services.plan_status_manager import PlanStatusManager, InvalidStateTransitionError
import uuid


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    from app.database import SessionLocal, engine, Base
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    db = SessionLocal()
    
    try:
        yield db
    finally:
        # 清理数据
        db.rollback()
        db.close()
        
        # 删除所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户"""
    user = User(
        id=str(uuid.uuid4()),
        email=f"test_{uuid.uuid4()}@example.com",
        nickname="测试用户",
        password_hash="hashed_password",
        age=25,
        gender="male",
        height=175.0,
        current_weight=80.0
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_plan(db_session: Session, test_user: User):
    """创建测试计划"""
    plan = BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=test_user.id,
        status=PlanStatus.PENDING,
        bet_amount=100.0,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        description="测试计划",
        creator_initial_weight=80.0,
        creator_target_weight=75.0,
        creator_target_weight_loss=5.0
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


class TestTransitionStatus:
    """测试 transition_status 方法"""
    
    def test_transition_pending_to_active(self, db_session: Session, test_plan: BettingPlan):
        """测试从 PENDING 转换到 ACTIVE"""
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.ACTIVE
        )
        
        assert result.status == PlanStatus.ACTIVE
        assert result.activated_at is not None
        
        # 验证数据库中的状态
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.ACTIVE
        assert test_plan.activated_at is not None
    
    def test_transition_pending_to_rejected(self, db_session: Session, test_plan: BettingPlan):
        """测试从 PENDING 转换到 REJECTED"""
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.REJECTED
        )
        
        assert result.status == PlanStatus.REJECTED
        
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.REJECTED
    
    def test_transition_pending_to_cancelled(self, db_session: Session, test_plan: BettingPlan, test_user: User):
        """测试从 PENDING 转换到 CANCELLED"""
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.CANCELLED,
            user_id=test_user.id
        )
        
        assert result.status == PlanStatus.CANCELLED
        assert result.abandoned_at is not None
        assert result.abandoned_by == test_user.id
        
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.CANCELLED
        assert test_plan.abandoned_at is not None
        assert test_plan.abandoned_by == test_user.id
    
    def test_transition_pending_to_expired(self, db_session: Session, test_plan: BettingPlan):
        """测试从 PENDING 转换到 EXPIRED"""
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.EXPIRED
        )
        
        assert result.status == PlanStatus.EXPIRED
        assert result.expiry_checked_at is not None
        
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.EXPIRED
    
    def test_transition_active_to_cancelled(self, db_session: Session, test_plan: BettingPlan, test_user: User):
        """测试从 ACTIVE 转换到 CANCELLED"""
        # 先转换到 ACTIVE
        test_plan.status = PlanStatus.ACTIVE
        db_session.commit()
        
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.ACTIVE,
            PlanStatus.CANCELLED,
            user_id=test_user.id
        )
        
        assert result.status == PlanStatus.CANCELLED
        assert result.abandoned_at is not None
        assert result.abandoned_by == test_user.id
    
    def test_transition_active_to_completed(self, db_session: Session, test_plan: BettingPlan):
        """测试从 ACTIVE 转换到 COMPLETED"""
        # 先转换到 ACTIVE
        test_plan.status = PlanStatus.ACTIVE
        db_session.commit()
        
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.ACTIVE,
            PlanStatus.COMPLETED
        )
        
        assert result.status == PlanStatus.COMPLETED
    
    def test_transition_active_to_expired(self, db_session: Session, test_plan: BettingPlan):
        """测试从 ACTIVE 转换到 EXPIRED"""
        # 先转换到 ACTIVE
        test_plan.status = PlanStatus.ACTIVE
        db_session.commit()
        
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.ACTIVE,
            PlanStatus.EXPIRED
        )
        
        assert result.status == PlanStatus.EXPIRED
        assert result.expiry_checked_at is not None
    
    def test_invalid_transition_pending_to_completed(self, db_session: Session, test_plan: BettingPlan):
        """测试非法转换: PENDING -> COMPLETED"""
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.PENDING,
                PlanStatus.COMPLETED
            )
        
        assert "非法的状态转换" in str(exc_info.value)
        
        # 验证状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.PENDING
    
    def test_invalid_transition_completed_to_active(self, db_session: Session, test_plan: BettingPlan):
        """测试非法转换: COMPLETED -> ACTIVE"""
        # 先设置为 COMPLETED
        test_plan.status = PlanStatus.COMPLETED
        db_session.commit()
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.COMPLETED,
                PlanStatus.ACTIVE
            )
        
        assert "非法的状态转换" in str(exc_info.value)
        
        # 验证状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.COMPLETED
    
    def test_invalid_transition_cancelled_to_active(self, db_session: Session, test_plan: BettingPlan):
        """测试非法转换: CANCELLED -> ACTIVE"""
        # 先设置为 CANCELLED
        test_plan.status = PlanStatus.CANCELLED
        db_session.commit()
        
        with pytest.raises(InvalidStateTransitionError):
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.CANCELLED,
                PlanStatus.ACTIVE
            )
        
        # 验证状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.CANCELLED
    
    def test_plan_not_found(self, db_session: Session):
        """测试计划不存在"""
        fake_plan_id = str(uuid.uuid4())
        
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.transition_status(
                db_session,
                fake_plan_id,
                PlanStatus.PENDING,
                PlanStatus.ACTIVE
            )
        
        assert "计划不存在" in str(exc_info.value)
    
    def test_status_mismatch(self, db_session: Session, test_plan: BettingPlan):
        """测试状态不匹配"""
        # 计划实际是 PENDING，但期望是 ACTIVE
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.ACTIVE,  # 期望状态错误
                PlanStatus.COMPLETED
            )
        
        assert "计划状态不匹配" in str(exc_info.value)
        
        # 验证状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.PENDING
    
    def test_transition_records_timestamp(self, db_session: Session, test_plan: BettingPlan):
        """测试状态转换记录时间戳"""
        before_time = datetime.now()
        
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.ACTIVE
        )
        
        after_time = datetime.now()
        
        assert result.activated_at is not None
        assert before_time <= result.activated_at <= after_time
    
    def test_transition_without_user_id(self, db_session: Session, test_plan: BettingPlan):
        """测试不提供 user_id 的状态转换"""
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.CANCELLED
        )
        
        assert result.status == PlanStatus.CANCELLED
        assert result.abandoned_at is not None
        assert result.abandoned_by is None  # 未提供 user_id



class TestAbandonPlan:
    """测试 abandon_plan 方法"""
    
    @pytest.fixture
    def second_user(self, db_session: Session):
        """创建第二个测试用户"""
        user = User(
            id=str(uuid.uuid4()),
            email=f"test2_{uuid.uuid4()}@example.com",
            nickname="测试用户2",
            password_hash="hashed_password",
            age=30,
            gender="female",
            height=165.0,
            current_weight=70.0
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def pending_plan_with_balance(self, db_session: Session, test_user: User):
        """创建带余额的待接受计划"""
        from app.models.balance import Balance
        from app.models.transaction import Transaction, TransactionType, TransactionStatus
        
        # 创建用户余额
        balance = Balance(
            user_id=test_user.id,
            available_balance=500.0,
            frozen_balance=100.0
        )
        db_session.add(balance)
        
        # 创建冻结交易记录
        plan_id = str(uuid.uuid4())
        transaction = Transaction(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        db_session.add(transaction)
        
        # 创建计划
        plan = BettingPlan(
            id=plan_id,
            creator_id=test_user.id,
            status=PlanStatus.PENDING,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            description="测试计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db_session.add(plan)
        db_session.commit()
        db_session.refresh(plan)
        return plan
    
    @pytest.fixture
    def active_plan_with_balance(self, db_session: Session, test_user: User, second_user: User):
        """创建带余额的进行中计划"""
        from app.models.balance import Balance
        from app.models.transaction import Transaction, TransactionType, TransactionStatus
        
        # 创建双方余额
        balance1 = Balance(
            user_id=test_user.id,
            available_balance=400.0,
            frozen_balance=100.0
        )
        balance2 = Balance(
            user_id=second_user.id,
            available_balance=400.0,
            frozen_balance=100.0
        )
        db_session.add(balance1)
        db_session.add(balance2)
        
        # 创建计划
        plan_id = str(uuid.uuid4())
        plan = BettingPlan(
            id=plan_id,
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            description="测试计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(plan)
        
        # 创建双方的冻结交易记录
        transaction1 = Transaction(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        transaction2 = Transaction(
            id=str(uuid.uuid4()),
            user_id=second_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        db_session.add(transaction1)
        db_session.add(transaction2)
        
        db_session.commit()
        db_session.refresh(plan)
        return plan
    
    def test_abandon_pending_plan_success(
        self, 
        db_session: Session, 
        pending_plan_with_balance: BettingPlan,
        test_user: User
    ):
        """测试成功放弃待接受计划"""
        from app.models.balance import Balance
        
        # 获取初始余额
        initial_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        initial_available = initial_balance.available_balance
        initial_frozen = initial_balance.frozen_balance
        
        # 放弃计划
        result = PlanStatusManager.abandon_plan(
            db_session,
            pending_plan_with_balance.id,
            test_user.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.plan_id == pending_plan_with_balance.id
        assert result.refunded_amount == 100.0
        assert "赌金已退还" in result.message
        
        # 验证计划状态
        db_session.refresh(pending_plan_with_balance)
        assert pending_plan_with_balance.status == PlanStatus.CANCELLED
        assert pending_plan_with_balance.abandoned_by == test_user.id
        assert pending_plan_with_balance.abandoned_at is not None
        
        # 验证余额变化
        final_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert final_balance.available_balance == initial_available + 100.0
        assert final_balance.frozen_balance == initial_frozen - 100.0
    
    def test_abandon_pending_plan_not_creator(
        self,
        db_session: Session,
        pending_plan_with_balance: BettingPlan,
        second_user: User
    ):
        """测试非创建者尝试放弃待接受计划"""
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.abandon_plan(
                db_session,
                pending_plan_with_balance.id,
                second_user.id
            )
        
        assert "只有创建者可以放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(pending_plan_with_balance)
        assert pending_plan_with_balance.status == PlanStatus.PENDING
    
    def test_abandon_active_plan_by_creator(
        self,
        db_session: Session,
        active_plan_with_balance: BettingPlan,
        test_user: User,
        second_user: User
    ):
        """测试创建者放弃进行中计划"""
        from app.models.balance import Balance
        
        # 获取初始余额
        creator_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        participant_balance = db_session.query(Balance).filter(
            Balance.user_id == second_user.id
        ).first()
        
        creator_initial = creator_balance.available_balance
        participant_initial = participant_balance.available_balance
        
        # 创建者放弃计划
        result = PlanStatusManager.abandon_plan(
            db_session,
            active_plan_with_balance.id,
            test_user.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.plan_id == active_plan_with_balance.id
        assert result.winner_id == second_user.id
        assert result.loser_id == test_user.id
        assert result.transferred_amount == 200.0
        assert "对方获胜" in result.message
        
        # 验证计划状态
        db_session.refresh(active_plan_with_balance)
        assert active_plan_with_balance.status == PlanStatus.CANCELLED
        assert active_plan_with_balance.abandoned_by == test_user.id
        assert active_plan_with_balance.abandoned_at is not None
        
        # 验证余额变化
        db_session.refresh(creator_balance)
        db_session.refresh(participant_balance)
        
        # 创建者: 解冻100，但不增加（因为转给对方）
        assert creator_balance.available_balance == creator_initial
        assert creator_balance.frozen_balance == 0.0
        
        # 参与者: 解冻100 + 收到创建者的100 = +200
        assert participant_balance.available_balance == participant_initial + 200.0
        assert participant_balance.frozen_balance == 0.0
    
    def test_abandon_active_plan_by_participant(
        self,
        db_session: Session,
        active_plan_with_balance: BettingPlan,
        test_user: User,
        second_user: User
    ):
        """测试参与者放弃进行中计划"""
        from app.models.balance import Balance
        
        # 获取初始余额
        creator_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        participant_balance = db_session.query(Balance).filter(
            Balance.user_id == second_user.id
        ).first()
        
        creator_initial = creator_balance.available_balance
        participant_initial = participant_balance.available_balance
        
        # 参与者放弃计划
        result = PlanStatusManager.abandon_plan(
            db_session,
            active_plan_with_balance.id,
            second_user.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.winner_id == test_user.id
        assert result.loser_id == second_user.id
        assert result.transferred_amount == 200.0
        
        # 验证计划状态
        db_session.refresh(active_plan_with_balance)
        assert active_plan_with_balance.status == PlanStatus.CANCELLED
        assert active_plan_with_balance.abandoned_by == second_user.id
        
        # 验证余额变化
        db_session.refresh(creator_balance)
        db_session.refresh(participant_balance)
        
        # 创建者获胜: 解冻100 + 收到参与者的100 = +200
        assert creator_balance.available_balance == creator_initial + 200.0
        assert creator_balance.frozen_balance == 0.0
        
        # 参与者失败: 解冻100，但转给创建者
        assert participant_balance.available_balance == participant_initial
        assert participant_balance.frozen_balance == 0.0
    
    def test_abandon_active_plan_non_participant(
        self,
        db_session: Session,
        active_plan_with_balance: BettingPlan
    ):
        """测试非参与者尝试放弃进行中计划"""
        # 创建第三个用户
        third_user = User(
            id=str(uuid.uuid4()),
            email=f"test3_{uuid.uuid4()}@example.com",
            nickname="测试用户3",
            password_hash="hashed_password",
            age=28,
            gender="male",
            height=180.0,
            current_weight=85.0
        )
        db_session.add(third_user)
        db_session.commit()
        
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.abandon_plan(
                db_session,
                active_plan_with_balance.id,
                third_user.id
            )
        
        assert "只有参与者可以放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(active_plan_with_balance)
        assert active_plan_with_balance.status == PlanStatus.ACTIVE
    
    def test_abandon_completed_plan(
        self,
        db_session: Session,
        test_plan: BettingPlan,
        test_user: User
    ):
        """测试放弃已完成的计划"""
        # 设置计划为已完成
        test_plan.status = PlanStatus.COMPLETED
        db_session.commit()
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            PlanStatusManager.abandon_plan(
                db_session,
                test_plan.id,
                test_user.id
            )
        
        assert "不允许放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.COMPLETED
    
    def test_abandon_cancelled_plan(
        self,
        db_session: Session,
        test_plan: BettingPlan,
        test_user: User
    ):
        """测试放弃已取消的计划"""
        # 设置计划为已取消
        test_plan.status = PlanStatus.CANCELLED
        db_session.commit()
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            PlanStatusManager.abandon_plan(
                db_session,
                test_plan.id,
                test_user.id
            )
        
        assert "不允许放弃" in str(exc_info.value)
    
    def test_abandon_plan_not_found(self, db_session: Session, test_user: User):
        """测试放弃不存在的计划"""
        fake_plan_id = str(uuid.uuid4())
        
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.abandon_plan(
                db_session,
                fake_plan_id,
                test_user.id
            )
        
        assert "计划不存在" in str(exc_info.value)
    
    def test_abandon_pending_plan_updates_invitation(
        self,
        db_session: Session,
        pending_plan_with_balance: BettingPlan,
        test_user: User,
        second_user: User
    ):
        """测试放弃待接受计划时更新邀请状态"""
        from app.models.invitation import Invitation, InvitationStatus
        
        # 创建邀请记录
        invitation = Invitation(
            id=str(uuid.uuid4()),
            plan_id=pending_plan_with_balance.id,
            inviter_id=test_user.id,
            invitee_email=second_user.email,
            invitee_id=second_user.id,
            status=InvitationStatus.PENDING,
            sent_at=datetime.utcnow()
        )
        db_session.add(invitation)
        db_session.commit()
        
        # 放弃计划
        result = PlanStatusManager.abandon_plan(
            db_session,
            pending_plan_with_balance.id,
            test_user.id
        )
        
        assert result.success is True
        
        # 验证邀请状态更新为 EXPIRED
        db_session.refresh(invitation)
        assert invitation.status == InvitationStatus.EXPIRED


class TestCheckExpiredPlans:
    """测试 check_expired_plans 方法"""
    
    @pytest.fixture
    def second_user(self, db_session: Session):
        """创建第二个测试用户"""
        user = User(
            id=str(uuid.uuid4()),
            email=f"test2_{uuid.uuid4()}@example.com",
            nickname="测试用户2",
            password_hash="hashed_password",
            age=30,
            gender="female",
            height=165.0,
            current_weight=70.0
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_check_expired_plans_marks_expired(
        self,
        db_session: Session,
        test_user: User,
        second_user: User
    ):
        """测试检查过期计划并标记为 EXPIRED"""
        # 创建一个已过期的 active 计划
        expired_plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=31),
            end_date=datetime.now() - timedelta(days=1),  # 昨天过期
            description="已过期计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(expired_plan)
        db_session.commit()
        
        # 执行检查
        expired_plans = PlanStatusManager.check_expired_plans(db_session)
        
        # 验证结果
        assert len(expired_plans) == 1
        assert expired_plans[0].id == expired_plan.id
        assert expired_plans[0].status == PlanStatus.EXPIRED
        assert expired_plans[0].expiry_checked_at is not None
        
        # 验证数据库中的状态
        db_session.refresh(expired_plan)
        assert expired_plan.status == PlanStatus.EXPIRED
        assert expired_plan.expiry_checked_at is not None
    
    def test_check_expired_plans_ignores_non_active(
        self,
        db_session: Session,
        test_user: User
    ):
        """测试检查过期计划时忽略非 ACTIVE 状态的计划"""
        # 创建一个已过期但状态为 PENDING 的计划
        pending_plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            status=PlanStatus.PENDING,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=31),
            end_date=datetime.now() - timedelta(days=1),
            description="待接受的过期计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db_session.add(pending_plan)
        db_session.commit()
        
        # 执行检查
        expired_plans = PlanStatusManager.check_expired_plans(db_session)
        
        # 验证结果 - 不应该标记 PENDING 计划
        assert len(expired_plans) == 0
        
        # 验证状态未改变
        db_session.refresh(pending_plan)
        assert pending_plan.status == PlanStatus.PENDING
    
    def test_check_expired_plans_ignores_future_plans(
        self,
        db_session: Session,
        test_user: User,
        second_user: User
    ):
        """测试检查过期计划时忽略未来结束的计划"""
        # 创建一个未来结束的 active 计划
        future_plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),  # 未来30天结束
            description="未来结束的计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(future_plan)
        db_session.commit()
        
        # 执行检查
        expired_plans = PlanStatusManager.check_expired_plans(db_session)
        
        # 验证结果 - 不应该标记未来的计划
        assert len(expired_plans) == 0
        
        # 验证状态未改变
        db_session.refresh(future_plan)
        assert future_plan.status == PlanStatus.ACTIVE
    
    def test_check_expired_plans_multiple_plans(
        self,
        db_session: Session,
        test_user: User,
        second_user: User
    ):
        """测试检查多个过期计划"""
        # 创建多个已过期的计划
        expired_plan1 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=31),
            end_date=datetime.now() - timedelta(days=1),
            description="过期计划1",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        
        expired_plan2 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=second_user.id,
            participant_id=test_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=200.0,
            start_date=datetime.now() - timedelta(days=61),
            end_date=datetime.now() - timedelta(days=31),
            description="过期计划2",
            creator_initial_weight=70.0,
            creator_target_weight=65.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=80.0,
            participant_target_weight=75.0,
            participant_target_weight_loss=5.0
        )
        
        db_session.add(expired_plan1)
        db_session.add(expired_plan2)
        db_session.commit()
        
        # 执行检查
        expired_plans = PlanStatusManager.check_expired_plans(db_session)
        
        # 验证结果
        assert len(expired_plans) == 2
        expired_plan_ids = {plan.id for plan in expired_plans}
        assert expired_plan1.id in expired_plan_ids
        assert expired_plan2.id in expired_plan_ids
        
        # 验证所有计划都被标记为 EXPIRED
        for plan in expired_plans:
            assert plan.status == PlanStatus.EXPIRED
            assert plan.expiry_checked_at is not None
    
    def test_check_expired_plans_sends_notifications(
        self,
        db_session: Session,
        test_user: User,
        second_user: User,
        monkeypatch
    ):
        """测试检查过期计划时发送通知"""
        # 记录通知调用
        notifications_sent = []
        
        def mock_send_notification(db, user_id, plan_id):
            notifications_sent.append({'user_id': user_id, 'plan_id': plan_id})
        
        # Mock 通知服务
        from app.services import notification_service
        monkeypatch.setattr(
            notification_service.NotificationService,
            'send_plan_expired_notification',
            mock_send_notification
        )
        
        # 创建一个已过期的 active 计划
        expired_plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=31),
            end_date=datetime.now() - timedelta(days=1),
            description="已过期计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(expired_plan)
        db_session.commit()
        
        # 执行检查
        expired_plans = PlanStatusManager.check_expired_plans(db_session)
        
        # 验证通知被发送
        assert len(expired_plans) == 1
        assert len(notifications_sent) == 2  # 创建者和参与者各一次
        
        # 验证通知参数
        user_ids_notified = {notif['user_id'] for notif in notifications_sent}
        assert test_user.id in user_ids_notified
        assert second_user.id in user_ids_notified
        
        # 验证 plan_id 参数
        for notif in notifications_sent:
            assert notif['plan_id'] == expired_plan.id
    
    def test_check_expired_plans_notification_failure_does_not_affect_status(
        self,
        db_session: Session,
        test_user: User,
        second_user: User,
        monkeypatch
    ):
        """测试通知发送失败不影响状态更新"""
        # Mock 通知服务使其抛出异常
        def mock_send_notification_error(db, user_id, plan_id):
            raise Exception("Notification service error")
        
        from app.services import notification_service
        monkeypatch.setattr(
            notification_service.NotificationService,
            'send_plan_expired_notification',
            mock_send_notification_error
        )
        
        # 创建一个已过期的 active 计划
        expired_plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=31),
            end_date=datetime.now() - timedelta(days=1),
            description="已过期计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(expired_plan)
        db_session.commit()
        
        # 执行检查 - 不应该抛出异常
        expired_plans = PlanStatusManager.check_expired_plans(db_session)
        
        # 验证状态仍然被更新
        assert len(expired_plans) == 1
        assert expired_plans[0].status == PlanStatus.EXPIRED
        
        # 验证数据库中的状态
        db_session.refresh(expired_plan)
        assert expired_plan.status == PlanStatus.EXPIRED


class TestMarkAsExpired:
    """测试 mark_as_expired 方法"""
    
    def test_mark_as_expired_success(self, db_session: Session, test_plan: BettingPlan):
        """测试成功标记计划为过期"""
        before_time = datetime.now()
        
        result = PlanStatusManager.mark_as_expired(db_session, test_plan.id)
        
        after_time = datetime.now()
        
        # 验证返回结果
        assert result.status == PlanStatus.EXPIRED
        assert result.expiry_checked_at is not None
        assert before_time <= result.expiry_checked_at <= after_time
        
        # 验证数据库中的状态
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.EXPIRED
        assert test_plan.expiry_checked_at is not None
    
    def test_mark_as_expired_plan_not_found(self, db_session: Session):
        """测试标记不存在的计划为过期"""
        fake_plan_id = str(uuid.uuid4())
        
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.mark_as_expired(db_session, fake_plan_id)
        
        assert "计划不存在" in str(exc_info.value)
    
    def test_mark_as_expired_from_active_status(self, db_session: Session, test_plan: BettingPlan):
        """测试从 ACTIVE 状态标记为过期"""
        # 先设置为 ACTIVE
        test_plan.status = PlanStatus.ACTIVE
        db_session.commit()
        
        result = PlanStatusManager.mark_as_expired(db_session, test_plan.id)
        
        assert result.status == PlanStatus.EXPIRED
        assert result.expiry_checked_at is not None
    
    def test_mark_as_expired_from_completed_status(self, db_session: Session, test_plan: BettingPlan):
        """测试从 COMPLETED 状态标记为过期（虽然不常见，但方法允许）"""
        # 先设置为 COMPLETED
        test_plan.status = PlanStatus.COMPLETED
        db_session.commit()
        
        result = PlanStatusManager.mark_as_expired(db_session, test_plan.id)
        
        # mark_as_expired 不验证状态，直接设置
        assert result.status == PlanStatus.EXPIRED


class TestPermissionValidation:
    """测试权限验证逻辑"""
    
    @pytest.fixture
    def second_user(self, db_session: Session):
        """创建第二个测试用户"""
        user = User(
            id=str(uuid.uuid4()),
            email=f"test2_{uuid.uuid4()}@example.com",
            nickname="测试用户2",
            password_hash="hashed_password",
            age=30,
            gender="female",
            height=165.0,
            current_weight=70.0
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def third_user(self, db_session: Session):
        """创建第三个测试用户"""
        user = User(
            id=str(uuid.uuid4()),
            email=f"test3_{uuid.uuid4()}@example.com",
            nickname="测试用户3",
            password_hash="hashed_password",
            age=28,
            gender="male",
            height=180.0,
            current_weight=85.0
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_pending_plan_only_creator_can_abandon(
        self,
        db_session: Session,
        test_plan: BettingPlan,
        second_user: User
    ):
        """测试待接受计划只有创建者可以放弃"""
        # test_plan 的创建者是 test_user，尝试用 second_user 放弃
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.abandon_plan(
                db_session,
                test_plan.id,
                second_user.id
            )
        
        assert "只有创建者可以放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.PENDING
    
    def test_active_plan_creator_can_abandon(
        self,
        db_session: Session,
        test_user: User,
        second_user: User
    ):
        """测试进行中计划创建者可以放弃"""
        from app.models.balance import Balance
        from app.models.transaction import Transaction, TransactionType, TransactionStatus
        
        # 创建双方余额
        balance1 = Balance(user_id=test_user.id, available_balance=400.0, frozen_balance=100.0)
        balance2 = Balance(user_id=second_user.id, available_balance=400.0, frozen_balance=100.0)
        db_session.add(balance1)
        db_session.add(balance2)
        
        # 创建 ACTIVE 计划
        plan_id = str(uuid.uuid4())
        plan = BettingPlan(
            id=plan_id,
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            description="测试计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(plan)
        
        # 创建冻结交易记录
        transaction1 = Transaction(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        transaction2 = Transaction(
            id=str(uuid.uuid4()),
            user_id=second_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        db_session.add(transaction1)
        db_session.add(transaction2)
        db_session.commit()
        
        # 创建者放弃计划 - 应该成功
        result = PlanStatusManager.abandon_plan(db_session, plan_id, test_user.id)
        
        assert result.success is True
        assert result.loser_id == test_user.id
        assert result.winner_id == second_user.id
    
    def test_active_plan_participant_can_abandon(
        self,
        db_session: Session,
        test_user: User,
        second_user: User
    ):
        """测试进行中计划参与者可以放弃"""
        from app.models.balance import Balance
        from app.models.transaction import Transaction, TransactionType, TransactionStatus
        
        # 创建双方余额
        balance1 = Balance(user_id=test_user.id, available_balance=400.0, frozen_balance=100.0)
        balance2 = Balance(user_id=second_user.id, available_balance=400.0, frozen_balance=100.0)
        db_session.add(balance1)
        db_session.add(balance2)
        
        # 创建 ACTIVE 计划
        plan_id = str(uuid.uuid4())
        plan = BettingPlan(
            id=plan_id,
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            description="测试计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(plan)
        
        # 创建冻结交易记录
        transaction1 = Transaction(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        transaction2 = Transaction(
            id=str(uuid.uuid4()),
            user_id=second_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan_id,
            completed_at=datetime.utcnow()
        )
        db_session.add(transaction1)
        db_session.add(transaction2)
        db_session.commit()
        
        # 参与者放弃计划 - 应该成功
        result = PlanStatusManager.abandon_plan(db_session, plan_id, second_user.id)
        
        assert result.success is True
        assert result.loser_id == second_user.id
        assert result.winner_id == test_user.id
    
    def test_active_plan_third_party_cannot_abandon(
        self,
        db_session: Session,
        test_user: User,
        second_user: User,
        third_user: User
    ):
        """测试进行中计划第三方用户不能放弃"""
        # 创建 ACTIVE 计划
        plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=test_user.id,
            participant_id=second_user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            description="测试计划",
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0
        )
        db_session.add(plan)
        db_session.commit()
        
        # 第三方用户尝试放弃 - 应该失败
        with pytest.raises(ValueError) as exc_info:
            PlanStatusManager.abandon_plan(db_session, plan.id, third_user.id)
        
        assert "只有参与者可以放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(plan)
        assert plan.status == PlanStatus.ACTIVE
    
    def test_cannot_abandon_rejected_plan(
        self,
        db_session: Session,
        test_plan: BettingPlan,
        test_user: User
    ):
        """测试不能放弃已拒绝的计划"""
        # 设置计划为 REJECTED
        test_plan.status = PlanStatus.REJECTED
        db_session.commit()
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            PlanStatusManager.abandon_plan(db_session, test_plan.id, test_user.id)
        
        assert "不允许放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.REJECTED
    
    def test_cannot_abandon_expired_plan(
        self,
        db_session: Session,
        test_plan: BettingPlan,
        test_user: User
    ):
        """测试不能放弃已过期的计划"""
        # 设置计划为 EXPIRED
        test_plan.status = PlanStatus.EXPIRED
        db_session.commit()
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            PlanStatusManager.abandon_plan(db_session, test_plan.id, test_user.id)
        
        assert "不允许放弃" in str(exc_info.value)
        
        # 验证计划状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.EXPIRED


class TestStateTransitionEdgeCases:
    """测试状态转换的边界情况"""
    
    def test_transition_rejected_to_any_state_fails(self, db_session: Session, test_plan: BettingPlan):
        """测试从 REJECTED 状态转换到任何状态都失败"""
        # 设置为 REJECTED
        test_plan.status = PlanStatus.REJECTED
        db_session.commit()
        
        # 尝试转换到 ACTIVE
        with pytest.raises(InvalidStateTransitionError):
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.REJECTED,
                PlanStatus.ACTIVE
            )
        
        # 尝试转换到 PENDING
        with pytest.raises(InvalidStateTransitionError):
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.REJECTED,
                PlanStatus.PENDING
            )
        
        # 验证状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.REJECTED
    
    def test_transition_expired_to_any_state_fails(self, db_session: Session, test_plan: BettingPlan):
        """测试从 EXPIRED 状态转换到任何状态都失败"""
        # 设置为 EXPIRED
        test_plan.status = PlanStatus.EXPIRED
        db_session.commit()
        
        # 尝试转换到 ACTIVE
        with pytest.raises(InvalidStateTransitionError):
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.EXPIRED,
                PlanStatus.ACTIVE
            )
        
        # 尝试转换到 COMPLETED
        with pytest.raises(InvalidStateTransitionError):
            PlanStatusManager.transition_status(
                db_session,
                test_plan.id,
                PlanStatus.EXPIRED,
                PlanStatus.COMPLETED
            )
        
        # 验证状态未改变
        db_session.refresh(test_plan)
        assert test_plan.status == PlanStatus.EXPIRED
    
    def test_all_valid_transitions_from_pending(self, db_session: Session, test_user: User):
        """测试从 PENDING 状态的所有合法转换"""
        valid_targets = [PlanStatus.ACTIVE, PlanStatus.REJECTED, PlanStatus.CANCELLED, PlanStatus.EXPIRED]
        
        for target_status in valid_targets:
            # 为每个转换创建新计划
            plan = BettingPlan(
                id=str(uuid.uuid4()),
                creator_id=test_user.id,
                status=PlanStatus.PENDING,
                bet_amount=100.0,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                description=f"测试计划 - {target_status.value}",
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db_session.add(plan)
            db_session.commit()
            
            # 执行转换
            result = PlanStatusManager.transition_status(
                db_session,
                plan.id,
                PlanStatus.PENDING,
                target_status,
                user_id=test_user.id if target_status == PlanStatus.CANCELLED else None
            )
            
            # 验证转换成功
            assert result.status == target_status
            db_session.refresh(plan)
            assert plan.status == target_status
    
    def test_all_valid_transitions_from_active(self, db_session: Session, test_user: User):
        """测试从 ACTIVE 状态的所有合法转换"""
        valid_targets = [PlanStatus.CANCELLED, PlanStatus.COMPLETED, PlanStatus.EXPIRED]
        
        for target_status in valid_targets:
            # 为每个转换创建新计划
            plan = BettingPlan(
                id=str(uuid.uuid4()),
                creator_id=test_user.id,
                status=PlanStatus.ACTIVE,
                bet_amount=100.0,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                description=f"测试计划 - {target_status.value}",
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db_session.add(plan)
            db_session.commit()
            
            # 执行转换
            result = PlanStatusManager.transition_status(
                db_session,
                plan.id,
                PlanStatus.ACTIVE,
                target_status,
                user_id=test_user.id if target_status == PlanStatus.CANCELLED else None
            )
            
            # 验证转换成功
            assert result.status == target_status
            db_session.refresh(plan)
            assert plan.status == target_status
    
    def test_transition_with_user_id_records_abandoner(
        self,
        db_session: Session,
        test_plan: BettingPlan,
        test_user: User
    ):
        """测试带 user_id 的转换记录放弃者"""
        result = PlanStatusManager.transition_status(
            db_session,
            test_plan.id,
            PlanStatus.PENDING,
            PlanStatus.CANCELLED,
            user_id=test_user.id
        )
        
        assert result.abandoned_by == test_user.id
        assert result.abandoned_at is not None
        
        db_session.refresh(test_plan)
        assert test_plan.abandoned_by == test_user.id
        assert test_plan.abandoned_at is not None
