"""
FundManager 单元测试
"""
import pytest
from sqlalchemy.orm import Session
from app.services.fund_manager import FundManager
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus
import uuid
from datetime import datetime, timedelta


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
    
    # 创建余额记录
    balance = Balance(
        user_id=user.id,
        available_balance=1000.0,
        frozen_balance=0.0
    )
    db_session.add(balance)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_plan(db_session: Session, test_user: User):
    """创建测试计划"""
    plan = BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=test_user.id,
        bet_amount=100.0,
        status=PlanStatus.PENDING,
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


class TestFreezeFunds:
    """测试 freeze_funds 方法"""
    
    def test_freeze_funds_success(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试成功冻结资金"""
        # 获取初始余额
        initial_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        initial_available = initial_balance.available_balance
        initial_frozen = initial_balance.frozen_balance
        
        # 执行冻结操作
        result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            100.0
        )
        
        # 验证结果
        assert result.success is True
        assert result.transaction_id is not None
        assert result.error is None
        
        # 验证余额变化
        updated_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert updated_balance.available_balance == initial_available - 100.0
        assert updated_balance.frozen_balance == initial_frozen + 100.0
        
        # 验证交易记录
        transaction = db_session.query(Transaction).filter(
            Transaction.id == result.transaction_id
        ).first()
        assert transaction is not None
        assert transaction.user_id == test_user.id
        assert transaction.type == TransactionType.FREEZE
        assert transaction.amount == 100.0
        assert transaction.status == TransactionStatus.COMPLETED
        assert transaction.related_plan_id == test_plan.id
        assert transaction.completed_at is not None
    
    def test_freeze_funds_insufficient_balance(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试余额不足时冻结失败"""
        # 尝试冻结超过可用余额的金额
        result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            2000.0  # 超过可用余额 1000.0
        )
        
        # 验证结果
        assert result.success is False
        assert result.transaction_id is None
        assert result.error == "余额不足"
        
        # 验证余额未变化
        balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert balance.available_balance == 1000.0
        assert balance.frozen_balance == 0.0
        
        # 验证没有创建交易记录
        transaction_count = db_session.query(Transaction).filter(
            Transaction.user_id == test_user.id,
            Transaction.type == TransactionType.FREEZE
        ).count()
        assert transaction_count == 0
    
    def test_freeze_funds_user_not_found(self, db_session: Session, test_plan: BettingPlan):
        """测试用户不存在时冻结失败"""
        non_existent_user_id = str(uuid.uuid4())
        
        result = FundManager.freeze_funds(
            db_session,
            non_existent_user_id,
            test_plan.id,
            100.0
        )
        
        # 验证结果
        assert result.success is False
        assert result.transaction_id is None
        assert result.error == "账户余额不存在"
    
    def test_freeze_funds_zero_amount(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试冻结零金额"""
        result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            0.0
        )
        
        # 验证结果 - 零金额应该成功
        assert result.success is True
        assert result.transaction_id is not None
        
        # 验证余额未变化
        balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert balance.available_balance == 1000.0
        assert balance.frozen_balance == 0.0
    
    def test_freeze_funds_exact_balance(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试冻结全部可用余额"""
        result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            1000.0  # 正好等于可用余额
        )
        
        # 验证结果
        assert result.success is True
        assert result.transaction_id is not None
        
        # 验证余额变化
        balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert balance.available_balance == 0.0
        assert balance.frozen_balance == 1000.0
    
    def test_freeze_funds_multiple_times(self, db_session: Session, test_user: User):
        """测试多次冻结资金"""
        plan1_id = str(uuid.uuid4())
        plan2_id = str(uuid.uuid4())
        
        # 第一次冻结
        result1 = FundManager.freeze_funds(
            db_session,
            test_user.id,
            plan1_id,
            300.0
        )
        assert result1.success is True
        
        # 第二次冻结
        result2 = FundManager.freeze_funds(
            db_session,
            test_user.id,
            plan2_id,
            400.0
        )
        assert result2.success is True
        
        # 验证余额
        balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert balance.available_balance == 300.0  # 1000 - 300 - 400
        assert balance.frozen_balance == 700.0  # 300 + 400
        
        # 验证交易记录数量
        transaction_count = db_session.query(Transaction).filter(
            Transaction.user_id == test_user.id,
            Transaction.type == TransactionType.FREEZE
        ).count()
        assert transaction_count == 2
    
    def test_freeze_funds_atomicity(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试冻结操作的原子性"""
        # 获取初始余额
        initial_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        initial_available = initial_balance.available_balance
        initial_frozen = initial_balance.frozen_balance
        
        # 执行冻结操作
        result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            100.0
        )
        
        # 验证总余额守恒
        updated_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        
        total_before = initial_available + initial_frozen
        total_after = updated_balance.available_balance + updated_balance.frozen_balance
        
        assert abs(total_before - total_after) < 0.01  # 允许浮点误差


class TestUnfreezeFunds:
    """测试 unfreeze_funds 方法"""
    
    def test_unfreeze_funds_success(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试成功解冻资金"""
        # 先冻结资金
        freeze_result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            100.0
        )
        assert freeze_result.success is True
        
        # 获取冻结后的余额
        balance_after_freeze = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        available_after_freeze = balance_after_freeze.available_balance
        frozen_after_freeze = balance_after_freeze.frozen_balance
        
        # 执行解冻操作
        result = FundManager.unfreeze_funds(
            db_session,
            test_user.id,
            test_plan.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.transaction_id is not None
        assert result.error is None
        
        # 验证余额变化
        updated_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert updated_balance.available_balance == available_after_freeze + 100.0
        assert updated_balance.frozen_balance == frozen_after_freeze - 100.0
        
        # 验证交易记录
        transaction = db_session.query(Transaction).filter(
            Transaction.id == result.transaction_id
        ).first()
        assert transaction is not None
        assert transaction.user_id == test_user.id
        assert transaction.type == TransactionType.UNFREEZE
        assert transaction.amount == 100.0
        assert transaction.status == TransactionStatus.COMPLETED
        assert transaction.related_plan_id == test_plan.id
    
    def test_unfreeze_funds_no_freeze_record(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试没有冻结记录时解冻失败"""
        result = FundManager.unfreeze_funds(
            db_session,
            test_user.id,
            test_plan.id
        )
        
        # 验证结果
        assert result.success is False
        assert result.transaction_id is None
        assert result.error == "未找到冻结记录"
    
    def test_unfreeze_funds_user_not_found(self, db_session: Session, test_plan: BettingPlan):
        """测试用户不存在时解冻失败"""
        non_existent_user_id = str(uuid.uuid4())
        
        result = FundManager.unfreeze_funds(
            db_session,
            non_existent_user_id,
            test_plan.id
        )
        
        # 验证结果
        assert result.success is False
        assert result.transaction_id is None
        assert result.error == "账户余额不存在"
    
    def test_unfreeze_funds_atomicity(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试解冻操作的原子性"""
        # 先冻结资金
        FundManager.freeze_funds(db_session, test_user.id, test_plan.id, 100.0)
        
        # 获取解冻前的总余额
        balance_before = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        total_before = balance_before.available_balance + balance_before.frozen_balance
        
        # 执行解冻操作
        result = FundManager.unfreeze_funds(
            db_session,
            test_user.id,
            test_plan.id
        )
        assert result.success is True
        
        # 验证总余额守恒
        balance_after = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        total_after = balance_after.available_balance + balance_after.frozen_balance
        
        assert abs(total_before - total_after) < 0.01  # 允许浮点误差


class TestTransferFunds:
    """测试 transfer_funds 方法"""
    
    def test_transfer_funds_success(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试成功转账"""
        # 创建第二个用户
        recipient = User(
            id=str(uuid.uuid4()),
            email=f"recipient_{uuid.uuid4()}@example.com",
            nickname="收款用户",
            password_hash="hashed_password",
            age=30,
            gender="female",
            height=165.0,
            current_weight=60.0
        )
        db_session.add(recipient)
        
        recipient_balance = Balance(
            user_id=recipient.id,
            available_balance=500.0,
            frozen_balance=0.0
        )
        db_session.add(recipient_balance)
        db_session.commit()
        
        # 记录初始余额值（不是对象引用）
        sender_initial_available = 1000.0  # test_user 的初始余额
        recipient_initial_available = 500.0
        
        # 执行转账操作
        result = FundManager.transfer_funds(
            db_session,
            test_user.id,
            recipient.id,
            200.0,
            test_plan.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.transaction_id is not None
        assert result.error is None
        
        # 验证余额变化
        sender_balance_after = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        recipient_balance_after = db_session.query(Balance).filter(
            Balance.user_id == recipient.id
        ).first()
        
        assert sender_balance_after.available_balance == sender_initial_available - 200.0
        assert recipient_balance_after.available_balance == recipient_initial_available + 200.0
        
        # 验证交易记录
        transaction = db_session.query(Transaction).filter(
            Transaction.id == result.transaction_id
        ).first()
        assert transaction is not None
        assert transaction.user_id == recipient.id
        assert transaction.type == TransactionType.TRANSFER
        assert transaction.amount == 200.0
        assert transaction.status == TransactionStatus.COMPLETED
    
    def test_transfer_funds_from_platform(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试从平台转账"""
        # 获取初始余额
        initial_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        initial_available = initial_balance.available_balance
        
        # 从平台转账
        result = FundManager.transfer_funds(
            db_session,
            "platform",
            test_user.id,
            300.0,
            test_plan.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.transaction_id is not None
        
        # 验证余额变化（只增加收款方余额）
        updated_balance = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert updated_balance.available_balance == initial_available + 300.0
    
    def test_transfer_funds_insufficient_balance(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试余额不足时转账失败"""
        # 创建收款用户
        recipient = User(
            id=str(uuid.uuid4()),
            email=f"recipient_{uuid.uuid4()}@example.com",
            nickname="收款用户",
            password_hash="hashed_password",
            age=30,
            gender="female",
            height=165.0,
            current_weight=60.0
        )
        db_session.add(recipient)
        
        recipient_balance = Balance(
            user_id=recipient.id,
            available_balance=500.0,
            frozen_balance=0.0
        )
        db_session.add(recipient_balance)
        db_session.commit()
        
        # 尝试转账超过可用余额的金额
        result = FundManager.transfer_funds(
            db_session,
            test_user.id,
            recipient.id,
            2000.0,  # 超过可用余额 1000.0
            test_plan.id
        )
        
        # 验证结果
        assert result.success is False
        assert result.transaction_id is None
        assert result.error == "付款账户余额不足"
    
    def test_transfer_funds_recipient_not_found(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试收款用户不存在时转账失败"""
        non_existent_user_id = str(uuid.uuid4())
        
        result = FundManager.transfer_funds(
            db_session,
            test_user.id,
            non_existent_user_id,
            100.0,
            test_plan.id
        )
        
        # 验证结果
        assert result.success is False
        assert result.transaction_id is None
        assert result.error == "收款账户余额不存在"
    
    def test_transfer_funds_atomicity(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试转账操作的原子性"""
        # 创建收款用户
        recipient = User(
            id=str(uuid.uuid4()),
            email=f"recipient_{uuid.uuid4()}@example.com",
            nickname="收款用户",
            password_hash="hashed_password",
            age=30,
            gender="female",
            height=165.0,
            current_weight=60.0
        )
        db_session.add(recipient)
        
        recipient_balance = Balance(
            user_id=recipient.id,
            available_balance=500.0,
            frozen_balance=0.0
        )
        db_session.add(recipient_balance)
        db_session.commit()
        
        # 获取转账前的总余额
        sender_balance_before = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        recipient_balance_before = db_session.query(Balance).filter(
            Balance.user_id == recipient.id
        ).first()
        total_before = (sender_balance_before.available_balance + 
                       sender_balance_before.frozen_balance +
                       recipient_balance_before.available_balance + 
                       recipient_balance_before.frozen_balance)
        
        # 执行转账操作
        result = FundManager.transfer_funds(
            db_session,
            test_user.id,
            recipient.id,
            200.0,
            test_plan.id
        )
        assert result.success is True
        
        # 验证总余额守恒
        sender_balance_after = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        recipient_balance_after = db_session.query(Balance).filter(
            Balance.user_id == recipient.id
        ).first()
        total_after = (sender_balance_after.available_balance + 
                      sender_balance_after.frozen_balance +
                      recipient_balance_after.available_balance + 
                      recipient_balance_after.frozen_balance)
        
        assert abs(total_before - total_after) < 0.01  # 允许浮点误差


class TestProcessAbandonRefund:
    """测试 process_abandon_refund 方法"""
    
    def test_abandon_pending_plan(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试放弃 pending 状态的计划"""
        # 先冻结创建者资金
        freeze_result = FundManager.freeze_funds(
            db_session,
            test_user.id,
            test_plan.id,
            100.0
        )
        assert freeze_result.success is True
        
        # 获取冻结后的余额
        balance_after_freeze = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        available_after_freeze = balance_after_freeze.available_balance
        frozen_after_freeze = balance_after_freeze.frozen_balance
        
        # 放弃计划
        result = FundManager.process_abandon_refund(
            db_session,
            test_plan,
            test_user.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.plan_id == test_plan.id
        assert result.refunded_amount == 100.0
        assert result.message == "计划已放弃，赌金已退还"
        
        # 验证余额恢复
        balance_after_abandon = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        assert balance_after_abandon.available_balance == available_after_freeze + 100.0
        assert balance_after_abandon.frozen_balance == frozen_after_freeze - 100.0
    
    def test_abandon_active_plan(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试放弃 active 状态的计划"""
        # 创建参与者
        participant = User(
            id=str(uuid.uuid4()),
            email=f"participant_{uuid.uuid4()}@example.com",
            nickname="参与者",
            password_hash="hashed_password",
            age=28,
            gender="male",
            height=180.0,
            current_weight=85.0
        )
        db_session.add(participant)
        
        participant_balance = Balance(
            user_id=participant.id,
            available_balance=1000.0,
            frozen_balance=0.0
        )
        db_session.add(participant_balance)
        db_session.commit()
        
        # 更新计划状态为 active
        test_plan.status = PlanStatus.ACTIVE
        test_plan.participant_id = participant.id
        db_session.commit()
        
        # 记录初始余额
        creator_initial_available = 1000.0
        participant_initial_available = 1000.0
        
        # 冻结双方资金
        FundManager.freeze_funds(db_session, test_user.id, test_plan.id, 100.0)
        FundManager.freeze_funds(db_session, participant.id, test_plan.id, 100.0)
        
        # 创建者放弃计划（参与者获胜）
        result = FundManager.process_abandon_refund(
            db_session,
            test_plan,
            test_user.id
        )
        
        # 验证结果
        assert result.success is True
        assert result.plan_id == test_plan.id
        assert result.winner_id == participant.id
        assert result.loser_id == test_user.id
        assert result.transferred_amount == 200.0
        assert result.message == "计划已放弃，对方获胜"
        
        # 验证余额变化
        creator_balance_after = db_session.query(Balance).filter(
            Balance.user_id == test_user.id
        ).first()
        participant_balance_after = db_session.query(Balance).filter(
            Balance.user_id == participant.id
        ).first()
        
        # 创建者：冻结余额被扣除（输了）
        assert creator_balance_after.frozen_balance == 0.0
        # 可用余额保持不变（冻结的钱被扣除了）
        assert creator_balance_after.available_balance == creator_initial_available - 100.0
        
        # 参与者：冻结余额解冻，并获得双倍赌金
        assert participant_balance_after.frozen_balance == 0.0
        # 可用余额应该增加双倍赌金（解冻自己的100，然后获得200，净增加200）
        assert participant_balance_after.available_balance == participant_initial_available + 200.0
    
    def test_abandon_invalid_status(self, db_session: Session, test_user: User, test_plan: BettingPlan):
        """测试放弃无效状态的计划"""
        # 设置计划为 completed 状态
        test_plan.status = PlanStatus.COMPLETED
        db_session.commit()
        
        # 尝试放弃计划
        result = FundManager.process_abandon_refund(
            db_session,
            test_plan,
            test_user.id
        )
        
        # 验证结果
        assert result.success is False
        assert "计划状态不允许放弃" in result.message
