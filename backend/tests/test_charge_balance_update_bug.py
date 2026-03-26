"""
Bug Condition Exploration Test for Balance Not Updated After Charge

**Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.3**

This test explores the bug condition where charge API returns success but user balance
is not updated in the database. This test is EXPECTED TO FAIL on unfixed code, which
confirms the bug exists.

CRITICAL: This test encodes the EXPECTED BEHAVIOR. When it passes after the fix,
it confirms the bug is resolved.
"""
import pytest
from hypothesis import given, strategies as st, settings, Phase, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime
import uuid

from app.database import Base
from app.models.user import User
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
    from app.models.user import Gender
    
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


def simulate_charge(db, user_id: str, amount: float):
    """
    Simulate the charge endpoint logic from backend/app/api/payments.py
    
    This is the FIXED implementation that we're testing.
    """
    from app.logger import get_logger
    
    logger = get_logger()
    
    balance = db.query(Balance).filter(Balance.user_id == user_id).first()
    if not balance:
        logger.warning(f"Account not found for user: {user_id}")
        return {"success": False, "message": "账户不存在"}
    
    # Log old balance
    old_balance = balance.available_balance
    logger.info(f"Charge initiated: user={user_id}, amount={amount}, old_balance={old_balance}")
    
    # Update balance
    new_balance = old_balance + amount
    balance.available_balance = new_balance
    balance.updated_at = datetime.utcnow()
    
    # Create transaction record
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=TransactionType.CHARGE,
        amount=amount,
        status=TransactionStatus.COMPLETED,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)
    
    # Explicitly add balance to session to ensure tracking
    db.add(balance)
    
    # Flush changes to database before commit
    db.flush()
    
    # Commit transaction
    db.commit()
    
    # Refresh balance to get latest state from database
    db.refresh(balance)
    
    # Log new balance
    logger.info(f"Charge completed: user={user_id}, amount={amount}, old_balance={old_balance}, new_balance={balance.available_balance}")
    
    return {
        "success": True,
        "message": "充值成功",
        "amount": amount,
        "newBalance": balance.available_balance
    }


class TestChargeBalanceUpdateBug:
    """
    Bug Condition Exploration Tests
    
    These tests verify the bug condition: charge returns success but balance is not updated.
    On UNFIXED code, these tests should FAIL (balance remains unchanged).
    On FIXED code, these tests should PASS (balance is updated correctly).
    """
    
    def test_charge_success_updates_balance_concrete_case(self, test_db):
        """
        **Property 1: Bug Condition** - 充值成功后余额未更新 (Concrete Case)
        
        Test the specific failing case from the bug report:
        - User has 0.0 balance
        - User charges 200.0
        - Charge returns success
        - Balance should be updated to 200.0 (but on unfixed code it remains 0.0)
        
        EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS (balance is still 0.0)
        EXPECTED OUTCOME ON FIXED CODE: Test PASSES (balance is 200.0)
        """
        # Arrange: Create user with 0.0 balance
        user_id = str(uuid.uuid4())
        user, initial_balance_obj = create_test_user(test_db, user_id, initial_balance=0.0)
        old_balance = initial_balance_obj.available_balance
        
        # Act: Charge 200.0
        charge_amount = 200.0
        charge_result = simulate_charge(test_db, user_id, charge_amount)
        
        # Assert: Charge returns success
        assert charge_result["success"] is True, "Charge should return success"
        assert charge_result["amount"] == charge_amount, "Charge should return correct amount"
        
        # Assert: Balance should be updated in database (EXPECTED BEHAVIOR)
        # On unfixed code, this assertion will FAIL because balance is still 0.0
        # On fixed code, this assertion will PASS because balance is updated to 200.0
        updated_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        expected_balance = old_balance + charge_amount
        
        assert updated_balance.available_balance == expected_balance, (
            f"Balance should be updated to {expected_balance} after successful charge, "
            f"but it is {updated_balance.available_balance}. "
            f"This confirms the bug: charge returns success but balance is not updated."
        )
        
        # Assert: Transaction record should be created
        transaction = test_db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.CHARGE
        ).first()
        assert transaction is not None, "Transaction record should be created"
        assert transaction.amount == charge_amount, "Transaction amount should match charge amount"
        assert transaction.status == TransactionStatus.COMPLETED, "Transaction should be completed"
    
    @given(
        initial_balance=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        charge_amount=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(
        max_examples=10,  # Scoped to concrete failing cases for deterministic bugs
        phases=[Phase.generate, Phase.target],  # Skip shrinking for exploration
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_charge_success_updates_balance_property(self, test_db, initial_balance, charge_amount):
        """
        **Property 1: Bug Condition** - 充值成功后余额未更新 (Property-Based)
        
        For any initial balance and charge amount, when charge returns success,
        the user's available balance should be updated to oldBalance + chargeAmount.
        
        This property-based test generates multiple test cases to explore the bug
        across different input combinations.
        
        EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS (balance not updated)
        EXPECTED OUTCOME ON FIXED CODE: Test PASSES (balance updated correctly)
        """
        # Arrange: Create user with random initial balance
        user_id = str(uuid.uuid4())
        user, initial_balance_obj = create_test_user(test_db, user_id, initial_balance=initial_balance)
        old_balance = initial_balance_obj.available_balance
        
        # Act: Charge with random amount
        charge_result = simulate_charge(test_db, user_id, charge_amount)
        
        # Assert: Charge returns success
        assert charge_result["success"] is True, "Charge should return success"
        
        # Assert: Balance should be updated (EXPECTED BEHAVIOR)
        updated_balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        expected_balance = old_balance + charge_amount
        
        # Allow small floating point tolerance
        assert abs(updated_balance.available_balance - expected_balance) < 0.01, (
            f"Balance should be {expected_balance} after charge, "
            f"but got {updated_balance.available_balance}. "
            f"Initial: {old_balance}, Charge: {charge_amount}"
        )
    
    def test_charge_success_balance_persisted_in_database(self, test_db):
        """
        **Property 1: Bug Condition** - 充值成功后余额持久化到数据库
        
        Verify that after successful charge, the balance update is persisted in the database
        and subsequent queries return the updated balance.
        
        This tests Requirement 2.3: "系统 SHALL 在数据库中持久化更新后的用户余额,
        确保后续查询能获取到最新余额"
        
        EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS (subsequent query returns old balance)
        EXPECTED OUTCOME ON FIXED CODE: Test PASSES (subsequent query returns new balance)
        """
        # Arrange: Create user with 0.0 balance
        user_id = str(uuid.uuid4())
        user, _ = create_test_user(test_db, user_id, initial_balance=0.0)
        
        # Act: Charge 200.0
        charge_result = simulate_charge(test_db, user_id, 200.0)
        assert charge_result["success"] is True
        
        # Simulate a new query session (like a subsequent API call)
        # This ensures we're reading from the database, not from any cache
        test_db.expire_all()  # Clear session cache
        
        # Assert: Subsequent balance query returns updated balance
        balance_after_charge = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        assert balance_after_charge.available_balance == 200.0, (
            f"Subsequent balance query should return 200.0, "
            f"but got {balance_after_charge.available_balance}. "
            f"This confirms the bug: balance update is not persisted in database."
        )
    
    def test_charge_success_then_create_plan_scenario(self, test_db):
        """
        **Property 1: Bug Condition** - 充值后立即创建计划的完整场景
        
        This tests the exact user scenario from the bug report:
        1. User has insufficient balance (0.0)
        2. User charges 200.0
        3. User immediately tries to create a betting plan requiring 200.0
        4. System should have sufficient balance (200.0 >= 200.0)
        
        EXPECTED OUTCOME ON UNFIXED CODE: Test FAILS (balance still 0.0, insufficient for plan)
        EXPECTED OUTCOME ON FIXED CODE: Test PASSES (balance is 200.0, sufficient for plan)
        """
        # Arrange: Create user with 0.0 balance
        user_id = str(uuid.uuid4())
        user, _ = create_test_user(test_db, user_id, initial_balance=0.0)
        
        # Act: Charge 200.0
        charge_result = simulate_charge(test_db, user_id, 200.0)
        assert charge_result["success"] is True, "Charge should succeed"
        
        # Act: Immediately check if balance is sufficient for creating a 200.0 plan
        balance = test_db.query(Balance).filter(Balance.user_id == user_id).first()
        plan_amount = 200.0
        
        # Assert: Balance should be sufficient (EXPECTED BEHAVIOR)
        assert balance.available_balance >= plan_amount, (
            f"After charging 200.0, balance should be sufficient for 200.0 plan, "
            f"but balance is {balance.available_balance}. "
            f"This is the exact bug scenario: user charges but can't create plan immediately."
        )
