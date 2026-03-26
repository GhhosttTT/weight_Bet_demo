"""
FundManager 属性测试
使用 Hypothesis 进行基于属性的测试
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from sqlalchemy.orm import Session
from app.services.fund_manager import FundManager
from app.models.balance import Balance
from app.models.user import User
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


def create_test_user_with_balance(db: Session, available: float, frozen: float):
    """创建测试用户和余额"""
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
    db.add(user)
    
    balance = Balance(
        user_id=user.id,
        available_balance=available,
        frozen_balance=frozen
    )
    db.add(balance)
    db.commit()
    db.refresh(user)
    
    return user


def get_total_balance(db: Session):
    """计算所有用户的总余额"""
    balances = db.query(Balance).all()
    total = sum(b.available_balance + b.frozen_balance for b in balances)
    return total


@given(
    bet_amount=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    initial_balance=st.floats(min_value=0.0, max_value=20000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_balance_conservation_freeze(db_session: Session, bet_amount: float, initial_balance: float):
    """
    Feature: invite-and-abandon-plan, Property 19: Total Balance Conservation
    
    For any freeze operation, the sum of all users' available_balance and 
    frozen_balance before and after the operation should be equal.
    
    Validates: Requirements 7.4, 9.9
    """
    # 假设余额充足
    assume(initial_balance >= bet_amount)
    
    # 创建用户
    user = create_test_user_with_balance(db_session, initial_balance, 0.0)
    plan_id = str(uuid.uuid4())
    
    # 计算操作前总余额
    total_before = get_total_balance(db_session)
    
    # 执行冻结操作
    result = FundManager.freeze_funds(db_session, user.id, plan_id, bet_amount)
    
    # 计算操作后总余额
    total_after = get_total_balance(db_session)
    
    # 验证总余额守恒（允许浮点误差）
    assert abs(total_before - total_after) < 0.01, f"Balance not conserved: {total_before} != {total_after}"
    
    # 如果操作成功，验证余额变化正确
    if result.success:
        balance = db_session.query(Balance).filter(Balance.user_id == user.id).first()
        assert abs(balance.available_balance - (initial_balance - bet_amount)) < 0.01
        assert abs(balance.frozen_balance - bet_amount) < 0.01


@given(
    bet_amount=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    initial_balance=st.floats(min_value=0.0, max_value=20000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_balance_conservation_unfreeze(db_session: Session, bet_amount: float, initial_balance: float):
    """
    Feature: invite-and-abandon-plan, Property 19: Total Balance Conservation
    
    For any unfreeze operation, the sum of all users' available_balance and 
    frozen_balance before and after the operation should be equal.
    
    Validates: Requirements 7.4, 9.9
    """
    # 假设余额充足
    assume(initial_balance >= bet_amount)
    
    # 创建用户并冻结资金
    user = create_test_user_with_balance(db_session, initial_balance, 0.0)
    plan_id = str(uuid.uuid4())
    
    freeze_result = FundManager.freeze_funds(db_session, user.id, plan_id, bet_amount)
    assume(freeze_result.success)
    
    # 计算操作前总余额
    total_before = get_total_balance(db_session)
    
    # 执行解冻操作
    result = FundManager.unfreeze_funds(db_session, user.id, plan_id)
    
    # 计算操作后总余额
    total_after = get_total_balance(db_session)
    
    # 验证总余额守恒
    assert abs(total_before - total_after) < 0.01, f"Balance not conserved: {total_before} != {total_after}"
    
    # 如果操作成功，验证余额恢复
    if result.success:
        balance = db_session.query(Balance).filter(Balance.user_id == user.id).first()
        assert abs(balance.available_balance - initial_balance) < 0.01
        assert abs(balance.frozen_balance) < 0.01


@given(
    transfer_amount=st.floats(min_value=1.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    sender_balance=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    recipient_balance=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_balance_conservation_transfer(
    db_session: Session,
    transfer_amount: float,
    sender_balance: float,
    recipient_balance: float
):
    """
    Feature: invite-and-abandon-plan, Property 19: Total Balance Conservation
    
    For any transfer operation, the sum of all users' available_balance and 
    frozen_balance before and after the operation should be equal.
    
    Validates: Requirements 7.4, 9.9
    """
    # 假设发送方余额充足
    assume(sender_balance >= transfer_amount)
    
    # 创建两个用户
    sender = create_test_user_with_balance(db_session, sender_balance, 0.0)
    recipient = create_test_user_with_balance(db_session, recipient_balance, 0.0)
    plan_id = str(uuid.uuid4())
    
    # 计算操作前总余额
    total_before = get_total_balance(db_session)
    
    # 执行转账操作
    result = FundManager.transfer_funds(
        db_session,
        sender.id,
        recipient.id,
        transfer_amount,
        plan_id
    )
    
    # 计算操作后总余额
    total_after = get_total_balance(db_session)
    
    # 验证总余额守恒
    assert abs(total_before - total_after) < 0.01, f"Balance not conserved: {total_before} != {total_after}"
    
    # 如果操作成功，验证余额变化正确
    if result.success:
        sender_balance_after = db_session.query(Balance).filter(
            Balance.user_id == sender.id
        ).first()
        recipient_balance_after = db_session.query(Balance).filter(
            Balance.user_id == recipient.id
        ).first()
        
        assert abs(sender_balance_after.available_balance - (sender_balance - transfer_amount)) < 0.01
        assert abs(recipient_balance_after.available_balance - (recipient_balance + transfer_amount)) < 0.01


@given(
    bet_amount=st.floats(min_value=1.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    initial_balance=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_freeze_requires_sufficient_balance(
    db_session: Session,
    bet_amount: float,
    initial_balance: float
):
    """
    Feature: invite-and-abandon-plan, Property 25: Acceptance Requires Sufficient Balance
    
    For any freeze operation, if the user's available balance is less than 
    the freeze amount, the operation should fail.
    
    Validates: Requirements 12.4, 12.5
    """
    # 创建用户
    user = create_test_user_with_balance(db_session, initial_balance, 0.0)
    plan_id = str(uuid.uuid4())
    
    # 执行冻结操作
    result = FundManager.freeze_funds(db_session, user.id, plan_id, bet_amount)
    
    # 验证结果
    if initial_balance < bet_amount:
        # 余额不足，应该失败
        assert result.success is False
        assert result.error == "余额不足"
    else:
        # 余额充足，应该成功
        assert result.success is True


@given(
    operations=st.lists(
        st.tuples(
            st.sampled_from(['freeze', 'unfreeze', 'transfer']),
            st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
        ),
        min_size=1,
        max_size=10
    ),
    initial_balance=st.floats(min_value=5000.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_balance_conservation_multiple_operations(
    db_session: Session,
    operations: list,
    initial_balance: float
):
    """
    Feature: invite-and-abandon-plan, Property 19: Total Balance Conservation
    
    For any sequence of fund operations, the sum of all users' available_balance 
    and frozen_balance should remain constant.
    
    Validates: Requirements 7.4, 9.9
    """
    # 创建两个用户
    user1 = create_test_user_with_balance(db_session, initial_balance, 0.0)
    user2 = create_test_user_with_balance(db_session, initial_balance, 0.0)
    
    # 记录初始总余额
    initial_total = get_total_balance(db_session)
    
    # 执行一系列操作
    plan_ids = []
    for op_type, amount in operations:
        plan_id = str(uuid.uuid4())
        plan_ids.append(plan_id)
        
        if op_type == 'freeze':
            FundManager.freeze_funds(db_session, user1.id, plan_id, amount)
        elif op_type == 'unfreeze' and plan_ids:
            # 只有在有冻结记录时才能解冻
            FundManager.unfreeze_funds(db_session, user1.id, plan_ids[0])
        elif op_type == 'transfer':
            FundManager.transfer_funds(db_session, user1.id, user2.id, amount, plan_id)
    
    # 验证最终总余额守恒
    final_total = get_total_balance(db_session)
    assert abs(initial_total - final_total) < 0.1, f"Balance not conserved after multiple operations: {initial_total} != {final_total}"


@given(
    bet_amount=st.floats(min_value=1.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    initial_balance=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_freeze_unfreeze_idempotent(
    db_session: Session,
    bet_amount: float,
    initial_balance: float
):
    """
    Property: Freeze followed by unfreeze should restore original balance
    
    For any user with sufficient balance, freezing an amount and then 
    unfreezing it should restore the original available and frozen balances.
    
    Validates: Requirements 7.1, 7.2
    """
    # 假设余额充足
    assume(initial_balance >= bet_amount)
    
    # 创建用户
    user = create_test_user_with_balance(db_session, initial_balance, 0.0)
    plan_id = str(uuid.uuid4())
    
    # 记录初始余额
    balance_before = db_session.query(Balance).filter(Balance.user_id == user.id).first()
    available_before = balance_before.available_balance
    frozen_before = balance_before.frozen_balance
    
    # 冻结资金
    freeze_result = FundManager.freeze_funds(db_session, user.id, plan_id, bet_amount)
    assume(freeze_result.success)
    
    # 解冻资金
    unfreeze_result = FundManager.unfreeze_funds(db_session, user.id, plan_id)
    
    # 验证余额恢复
    if unfreeze_result.success:
        balance_after = db_session.query(Balance).filter(Balance.user_id == user.id).first()
        assert abs(balance_after.available_balance - available_before) < 0.01
        assert abs(balance_after.frozen_balance - frozen_before) < 0.01
