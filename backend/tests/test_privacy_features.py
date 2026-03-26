"""
数据隐私功能测试
"""
import pytest
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base
from app.models.user import User, Gender
from app.models.balance import Balance
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.check_in import CheckIn, ReviewStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.audit_log import AuditLog
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from fastapi import HTTPException


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    user = User(
        id="test_user_1",
        email="test@example.com",
        password_hash="hashed_password",
        nickname="测试用户",
        gender=Gender.MALE,
        age=25,
        height=175.0,
        current_weight=70.0,
        target_weight=65.0
    )
    db.add(user)
    
    # 创建余额记录
    balance = Balance(
        user_id=user.id,
        available_balance=100.0,
        frozen_balance=0.0
    )
    db.add(balance)
    
    db.commit()
    return user


class TestAuditLogService:
    """审计日志服务测试"""
    
    def test_log_action(self, db: Session, test_user: User):
        """测试记录审计日志"""
        audit_log = AuditService.log_action(
            db=db,
            action="user.login",
            resource_type="user",
            user_id=test_user.id,
            resource_id=test_user.id,
            details={"method": "email"},
            ip_address="127.0.0.1",
            user_agent="TestAgent/1.0"
        )
        
        assert audit_log.id is not None
        assert audit_log.action == "user.login"
        assert audit_log.resource_type == "user"
        assert audit_log.user_id == test_user.id
        assert audit_log.details["method"] == "email"
        assert audit_log.ip_address == "127.0.0.1"
    
    def test_query_logs(self, db: Session, test_user: User):
        """测试查询审计日志"""
        # 创建多条日志
        for i in range(5):
            AuditService.log_action(
                db=db,
                action=f"test.action_{i}",
                resource_type="test",
                user_id=test_user.id
            )
        
        # 查询所有日志
        logs = AuditService.query_logs(
            db=db,
            user_id=test_user.id,
            limit=10
        )
        
        assert len(logs) >= 5
        
        # 按操作类型查询
        logs = AuditService.query_logs(
            db=db,
            user_id=test_user.id,
            action="test.action_0"
        )
        
        assert len(logs) >= 1
        assert logs[0].action == "test.action_0"


class TestDataExport:
    """数据导出功能测试"""
    
    def test_export_user_data(self, db: Session, test_user: User):
        """测试导出用户数据"""
        # 创建一些测试数据
        plan = BettingPlan(
            id="test_plan_1",
            creator_id=test_user.id,
            status=PlanStatus.COMPLETED,
            bet_amount=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),
            creator_initial_weight=70.0,
            creator_target_weight=65.0,
            creator_target_weight_loss=5.0
        )
        db.add(plan)
        
        check_in = CheckIn(
            id="test_checkin_1",
            user_id=test_user.id,
            plan_id=plan.id,
            weight=69.0,
            check_in_date=datetime.utcnow().date(),
            review_status=ReviewStatus.APPROVED
        )
        db.add(check_in)
        
        transaction = Transaction(
            id="test_transaction_1",
            user_id=test_user.id,
            type=TransactionType.FREEZE,
            amount=100.0,
            status=TransactionStatus.COMPLETED,
            related_plan_id=plan.id
        )
        db.add(transaction)
        
        db.commit()
        
        # 导出数据
        export_data = UserService.export_user_data(
            db=db,
            user_id=test_user.id,
            current_user_id=test_user.id
        )
        
        # 验证导出数据
        assert export_data["user"]["id"] == test_user.id
        assert export_data["user"]["email"] == test_user.email
        assert export_data["balance"]["available_balance"] == 100.0
        assert len(export_data["betting_plans"]["as_creator"]) >= 1
        assert len(export_data["check_ins"]) >= 1
        assert len(export_data["transactions"]) >= 1
        
        # 验证可以序列化为JSON
        json_str = json.dumps(export_data)
        assert json_str is not None
    
    def test_export_permission_denied(self, db: Session, test_user: User):
        """测试导出权限验证"""
        with pytest.raises(HTTPException) as exc_info:
            UserService.export_user_data(
                db=db,
                user_id=test_user.id,
                current_user_id="other_user"
            )
        
        assert exc_info.value.status_code == 403


class TestAccountDeletion:
    """账户删除功能测试"""
    
    def test_delete_user_account(self, db: Session):
        """测试删除用户账户"""
        # 创建测试用户
        user = User(
            id="test_user_delete",
            email="delete@example.com",
            password_hash="hashed_password",
            nickname="待删除用户",
            gender=Gender.FEMALE,
            age=30,
            height=165.0,
            current_weight=60.0
        )
        db.add(user)
        
        balance = Balance(
            user_id=user.id,
            available_balance=50.0,
            frozen_balance=0.0
        )
        db.add(balance)
        
        db.commit()
        
        # 删除账户
        UserService.delete_user_account(
            db=db,
            user_id=user.id,
            current_user_id=user.id
        )
        
        # 验证数据已匿名化
        deleted_user = db.query(User).filter(User.id == user.id).first()
        assert deleted_user.email.startswith("deleted_")
        assert deleted_user.nickname.startswith("已删除用户_")
        assert deleted_user.password_hash == "DELETED"
        assert deleted_user.payment_method_id is None
        
        # 验证余额已清空
        deleted_balance = db.query(Balance).filter(Balance.user_id == user.id).first()
        assert deleted_balance.available_balance == 0.0
        assert deleted_balance.frozen_balance == 0.0
    
    def test_delete_with_active_plan(self, db: Session):
        """测试有活跃计划时无法删除"""
        user = User(
            id="test_user_active",
            email="active@example.com",
            password_hash="hashed_password",
            nickname="活跃用户",
            gender=Gender.MALE,
            age=28,
            height=180.0,
            current_weight=75.0
        )
        db.add(user)
        
        balance = Balance(
            user_id=user.id,
            available_balance=100.0,
            frozen_balance=0.0
        )
        db.add(balance)
        
        # 创建活跃计划
        plan = BettingPlan(
            id="active_plan",
            creator_id=user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),
            creator_initial_weight=75.0,
            creator_target_weight=70.0,
            creator_target_weight_loss=5.0
        )
        db.add(plan)
        db.commit()
        
        # 尝试删除账户
        with pytest.raises(HTTPException) as exc_info:
            UserService.delete_user_account(
                db=db,
                user_id=user.id,
                current_user_id=user.id
            )
        
        assert exc_info.value.status_code == 400
        assert "进行中的对赌计划" in exc_info.value.detail
    
    def test_delete_with_frozen_balance(self, db: Session):
        """测试有冻结余额时无法删除"""
        user = User(
            id="test_user_frozen",
            email="frozen@example.com",
            password_hash="hashed_password",
            nickname="冻结用户",
            gender=Gender.MALE,
            age=26,
            height=170.0,
            current_weight=68.0
        )
        db.add(user)
        
        balance = Balance(
            user_id=user.id,
            available_balance=50.0,
            frozen_balance=100.0  # 有冻结余额
        )
        db.add(balance)
        db.commit()
        
        # 尝试删除账户
        with pytest.raises(HTTPException) as exc_info:
            UserService.delete_user_account(
                db=db,
                user_id=user.id,
                current_user_id=user.id
            )
        
        assert exc_info.value.status_code == 400
        assert "冻结资金" in exc_info.value.detail
    
    def test_delete_permission_denied(self, db: Session, test_user: User):
        """测试删除权限验证"""
        with pytest.raises(HTTPException) as exc_info:
            UserService.delete_user_account(
                db=db,
                user_id=test_user.id,
                current_user_id="other_user"
            )
        
        assert exc_info.value.status_code == 403
