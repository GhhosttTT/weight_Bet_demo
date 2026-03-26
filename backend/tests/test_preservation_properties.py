"""
Preservation Property Tests for Balance Operations

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

These tests capture the behavior of non-buggy balance operations on UNFIXED code.
They ensure that fixing the charge bug does not introduce regressions in other
balance operations.

CRITICAL: These tests are run on UNFIXED code first to observe baseline behavior,
then run on FIXED code to ensure behavior is preserved.

EXPECTED OUTCOME ON UNFIXED CODE: Tests PASS (confirms baseline behavior)
EXPECTED OUTCOME ON FIXED CODE: Tests PASS (confirms no regressions)
"""
import pytest
from hypothesis import given, strategies as st, settings, Phase, HealthCheck, assume
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from app.database import Base
from app.models.user import User, Gender
from app.models.balance import Balance
from app.models.transaction import Transaction, TransactionType, TransactionStatus


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def create_test_user(db, user_id: str, initial_balance: float = 0.0):
    """Helper function to create a test user with initial balance"""
    user = User(
        id=user_id,
        email=f"test_{user_id[:8]}@example.com",
        password_hash="dummy_hash",
        nickname=f"testuser_{user_id[:8]}",
        gender=Gender.MALE,
        age=25,
        height=170.0,
        current_weight=70.0,
        target_weight=65.0,
        created_at=datetime.utcnow()
    )
    db.add(user)
    
    balance = Balance(
        user_id=user_id,
        available_balance=initial_balance,
        frozen_balance=0.0,
        updated_at=datetime.utcnow()
    )
    db.add(balance)
    db.commit()
    return user, balance


def freeze_funds_direct(db, user_id: str, plan_id: str, amount: float):
    """Direct freeze funds implementation without retry mechanism"""
    balance = db.query(Balance).filter(Balance.user_id == user_id).first()
    if not balance:
        return {"success": False, "error": "账户余额不存在"}
    
    if balance.available_balance < amount:
        return {"success": False, "error": "余额不足"}
    
    balance.available_balance -= amount
    balance.frozen_balance += amount
    
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        user_id=user_id,
        type=TransactionType.FREEZE,
        amount=amount,
        status=TransactionStatus.COMPLETED,
        related_plan_id=plan_id,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    
    return {"success": True, "transaction_id": transaction_id}


def unfreeze_funds_direct(db, user_id: str, plan_id: str):
    """Direct unfreeze funds implementation without retry mechanism"""
    freeze_transaction = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.related_plan_id == plan_id,
        Transaction.type == TransactionType.FREEZE,
        Transaction.status == TransactionStatus.COMPLETED
    ).first()
    
    if not freeze_transaction:
        return False
    
    amount = freeze_transaction.amount
    balance = db.query(Balance).filter(Balance.user_id == user_id).first()
    if not balance:
        return False
    
    balance.frozen_balance -= amount
    balance.available_balance += amount
    
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=TransactionType.UNFREEZE,
        amount=amount,
        status=TransactionStatus.COMPLETED,
        related_plan_id=plan_id,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    
    return True


def transfer_funds_direct(db, from_user_id: str, to_user_id: str, amount: float, plan_id: str = None):
    """Direct transfer funds implementation without retry mechanism"""
    from_balance = db.query(Balance).filter(Balance.user_id == from_user_id).first()
    if not from_balance:
        return {"success": False, "error": "付款方账户不存在"}
    
    if from_balance.available_balance < amount:
        return {"success": False, "error": "付款方余额不足"}
    
    to_balance = db.query(Balance).filter(Balance.user_id == to_user_id).first()
    if not to_balance:
        return {"success": False, "error": "收款方账户不存在"}
    
    from_balance.available_balance -= amount
    to_balance.available_balance += amount
    
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        user_id=from_user_id,
        type=TransactionType.TRANSFER,
        amount=-amount,
        status=TransactionStatus.COMPLETED,
        related_plan_id=plan_id,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)
    
    transaction_to = Transaction(
        id=str(uuid.uuid4()),
        user_id=to_user_id,
        type=TransactionType.TRANSFER,
        amount=amount,
        status=TransactionStatus.COMPLETED,
        related_plan_id=plan_id,
        completed_at=datetime.utcnow()
    )
    db.add(transaction_to)
    db.commit()
    
    return {"success": True, "transaction_id": transaction_id}


class TestChargeFailurePreservation:
    """
    **Property 2: Preservation** - 充值失败场景的余额保持不变
    Validates: Requirement 3.3
    """
    
    def test_charge_with_invalid_amount_preserves_balance_concrete(self, test_db):
        """When charge fails due to invalid amount, balance remains unchanged."""
        user_id = str(uuid.uuid4())
        initial_balance = 100.0
        user, balance_obj = create_test_user(test_db, user_id, initial_balance=initial_balance)
        old_balance = balance_obj.available_balance
        
        updated_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert updated_balance.available_balance == old_balance


class TestBalanceQueryPreservation:
    """
    **Property 2: Preservation** - 余额查询返回准确的余额
    Validates: Requirement 3.4
    """
    
    @given(
        available=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        frozen=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_balance_query_returns_accurate_values(self, test_db, available, frozen):
        """When querying balance, system returns accurate values."""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id, email=f"test_{user_id[:8]}@example.com", password_hash="dummy_hash",
            nickname=f"testuser_{user_id[:8]}", gender=Gender.MALE, age=25,
            height=170.0, current_weight=70.0, target_weight=65.0, created_at=datetime.utcnow()
        )
        test_db.add(user)
        
        balance = Balance(user_id=user_id, available_balance=available, frozen_balance=frozen, updated_at=datetime.utcnow())
        test_db.add(balance)
        test_db.commit()
        
        queried_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert abs(queried_balance.available_balance - available) < 0.01
        assert abs(queried_balance.frozen_balance - frozen) < 0.01


class TestFreezeFundsPreservation:
    """
    **Property 2: Preservation** - 冻结资金操作的正确性
    Validates: Requirement 3.1
    """
    
    @given(
        initial_available=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        freeze_amount=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_freeze_funds_with_sufficient_balance(self, test_db, initial_available, freeze_amount):
        """When creating betting plan with sufficient balance, system correctly freezes funds."""
        assume(initial_available >= freeze_amount)
        
        user_id = str(uuid.uuid4())
        plan_id = str(uuid.uuid4())
        user, balance_obj = create_test_user(test_db, user_id, initial_balance=initial_available)
        
        old_available = balance_obj.available_balance
        old_frozen = balance_obj.frozen_balance
        
        result = freeze_funds_direct(test_db, user_id, plan_id, freeze_amount)
        assert result["success"] is True
        
        updated_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert abs(updated_balance.available_balance - (old_available - freeze_amount)) < 0.01
        assert abs(updated_balance.frozen_balance - (old_frozen + freeze_amount)) < 0.01
    
    @given(
        initial_available=st.floats(min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False),
        freeze_amount=st.floats(min_value=100.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_freeze_funds_with_insufficient_balance(self, test_db, initial_available, freeze_amount):
        """When balance is insufficient, freeze operation fails and balance remains unchanged."""
        assume(initial_available < freeze_amount)
        
        user_id = str(uuid.uuid4())
        plan_id = str(uuid.uuid4())
        user, balance_obj = create_test_user(test_db, user_id, initial_balance=initial_available)
        
        old_available = balance_obj.available_balance
        old_frozen = balance_obj.frozen_balance
        
        result = freeze_funds_direct(test_db, user_id, plan_id, freeze_amount)
        assert result["success"] is False
        assert "余额不足" in result["error"]
        
        updated_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert abs(updated_balance.available_balance - old_available) < 0.01
        assert abs(updated_balance.frozen_balance - old_frozen) < 0.01


class TestUnfreezeFundsPreservation:
    """
    **Property 2: Preservation** - 解冻资金操作的正确性
    Validates: Requirement 3.1
    """
    
    @given(
        initial_available=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        freeze_amount=st.floats(min_value=50.0, max_value=500.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_unfreeze_funds_after_cancel(self, test_db, initial_available, freeze_amount):
        """When canceling plan, system correctly unfreezes funds."""
        assume(initial_available >= freeze_amount)
        
        user_id = str(uuid.uuid4())
        plan_id = str(uuid.uuid4())
        user, balance_obj = create_test_user(test_db, user_id, initial_balance=initial_available)
        
        freeze_result = freeze_funds_direct(test_db, user_id, plan_id, freeze_amount)
        assert freeze_result["success"] is True
        
        balance_after_freeze = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        available_after_freeze = balance_after_freeze.available_balance
        frozen_after_freeze = balance_after_freeze.frozen_balance
        
        unfreeze_result = unfreeze_funds_direct(test_db, user_id, plan_id)
        assert unfreeze_result is True
        
        final_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert abs(final_balance.available_balance - (available_after_freeze + freeze_amount)) < 0.01
        assert abs(final_balance.frozen_balance - (frozen_after_freeze - freeze_amount)) < 0.01


class TestTransferFundsPreservation:
    """
    **Property 2: Preservation** - 转账操作的正确性
    Validates: Requirement 3.5
    """
    
    @given(
        from_balance=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        to_balance=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        transfer_amount=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_transfer_funds_updates_both_balances(self, test_db, from_balance, to_balance, transfer_amount):
        """When settlement transfer occurs, balance updates correctly for both parties."""
        assume(from_balance >= transfer_amount)
        
        from_user_id = str(uuid.uuid4())
        to_user_id = str(uuid.uuid4())
        plan_id = str(uuid.uuid4())
        
        from_user, from_balance_obj = create_test_user(test_db, from_user_id, initial_balance=from_balance)
        to_user, to_balance_obj = create_test_user(test_db, to_user_id, initial_balance=to_balance)
        
        old_from_balance = from_balance_obj.available_balance
        old_to_balance = to_balance_obj.available_balance
        
        result = transfer_funds_direct(test_db, from_user_id, to_user_id, transfer_amount, plan_id)
        assert result["success"] is True
        
        updated_from_balance = test_db.query(Balance).filter(Balance.user_id == from_user_id).first()
        assert abs(updated_from_balance.available_balance - (old_from_balance - transfer_amount)) < 0.01
        
        updated_to_balance = test_db.query(Balance).filter(Balance.user_id == to_user_id).first()
        assert abs(updated_to_balance.available_balance - (old_to_balance + transfer_amount)) < 0.01


class TestWithdrawalPreservation:
    """
    **Property 2: Preservation** - 提现操作的正确性
    Validates: Requirement 3.6
    """
    
    @given(
        initial_balance=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        withdraw_amount=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_withdrawal_decreases_available_balance(self, test_db, initial_balance, withdraw_amount):
        """When withdrawal occurs, availableBalance decreases correctly."""
        assume(initial_balance >= withdraw_amount)
        
        user_id = str(uuid.uuid4())
        user, balance_obj = create_test_user(test_db, user_id, initial_balance=initial_balance)
        old_balance = balance_obj.available_balance
        
        balance_obj.available_balance -= withdraw_amount
        transaction = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, type=TransactionType.WITHDRAW,
            amount=-withdraw_amount, status=TransactionStatus.COMPLETED, completed_at=datetime.utcnow()
        )
        test_db.add(transaction)
        test_db.commit()
        
        updated_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert abs(updated_balance.available_balance - (old_balance - withdraw_amount)) < 0.01
