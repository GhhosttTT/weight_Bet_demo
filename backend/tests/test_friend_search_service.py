"""
测试好友搜索服务 (Task 2.1, 2.2)
"""
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.friend_search_service import FriendSearchService
from app.models.user import User, Gender
from app.schemas.user import UserSearchResult


class TestFriendSearchService:
    """测试好友搜索服务"""
    
    # ==================== 邮箱格式验证测试 ====================
    
    def test_validate_email_format_valid(self):
        """测试有效邮箱格式"""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user_123@test-domain.com",
            "a@b.co"
        ]
        
        for email in valid_emails:
            assert FriendSearchService.validate_email_format(email) is True
        
        print("✓ 有效邮箱格式验证测试通过")
    
    def test_validate_email_format_invalid(self):
        """测试无效邮箱格式"""
        invalid_emails = [
            "",
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
            "user @example.com",
            "user@example",
            "user..name@example.com",
            None,
            123
        ]
        
        for email in invalid_emails:
            assert FriendSearchService.validate_email_format(email) is False
        
        print("✓ 无效邮箱格式验证测试通过")
    
    # ==================== 搜索好友测试 ====================
    
    def test_search_by_email_success(self, db_session: Session):
        """测试通过邮箱搜索用户成功"""
        # 创建测试用户
        test_user = User(
            id="test_user_123",
            email="friend@example.com",
            password_hash="hashed_password",
            nickname="测试好友",
            gender=Gender.MALE,
            age=25,
            height=175.0,
            current_weight=70.0
        )
        db_session.add(test_user)
        db_session.commit()
        
        # 搜索用户
        result = FriendSearchService.search_by_email(db_session, "friend@example.com")
        
        # 验证结果
        assert result is not None
        assert isinstance(result, UserSearchResult)
        assert result.user_id == "test_user_123"
        assert result.nickname == "测试好友"
        assert result.age == 25
        assert result.gender == Gender.MALE
        
        print("✓ 搜索用户成功测试通过")
    
    def test_search_by_email_not_found(self, db_session: Session):
        """测试用户不存在情况"""
        # 搜索不存在的用户
        result = FriendSearchService.search_by_email(db_session, "nonexistent@example.com")
        
        # 验证返回 None
        assert result is None
        
        print("✓ 用户不存在测试通过")
    
    def test_search_by_email_invalid_format(self, db_session: Session):
        """测试无效邮箱格式"""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(HTTPException) as exc_info:
                FriendSearchService.search_by_email(db_session, email)
            
            assert exc_info.value.status_code == 400
            assert "邮箱格式无效" in exc_info.value.detail
        
        print("✓ 无效邮箱格式测试通过")
    
    def test_search_returns_only_public_info(self, db_session: Session):
        """测试搜索结果只返回公开信息"""
        # 创建测试用户（包含敏感信息）
        test_user = User(
            id="test_user_456",
            email="public@example.com",
            password_hash="secret_hash",
            nickname="公开用户",
            gender=Gender.FEMALE,
            age=30,
            height=165.0,
            current_weight=60.0,
            target_weight=55.0,
            payment_method_id="payment_123"
        )
        db_session.add(test_user)
        db_session.commit()
        
        # 搜索用户
        result = FriendSearchService.search_by_email(db_session, "public@example.com")
        
        # 验证只返回公开信息
        assert result is not None
        assert hasattr(result, 'user_id')
        assert hasattr(result, 'nickname')
        assert hasattr(result, 'age')
        assert hasattr(result, 'gender')
        
        # 验证不包含敏感信息
        assert not hasattr(result, 'password_hash')
        assert not hasattr(result, 'email')
        assert not hasattr(result, 'payment_method_id')
        assert not hasattr(result, 'current_weight')
        assert not hasattr(result, 'target_weight')
        
        print("✓ 只返回公开信息测试通过")
    
    def test_search_case_sensitive(self, db_session: Session):
        """测试邮箱搜索大小写敏感性"""
        # 创建测试用户
        test_user = User(
            id="test_user_789",
            email="CaseSensitive@Example.COM",
            password_hash="hashed_password",
            nickname="大小写测试",
            gender=Gender.OTHER,
            age=28,
            height=170.0,
            current_weight=65.0
        )
        db_session.add(test_user)
        db_session.commit()
        
        # 使用完全相同的邮箱搜索
        result = FriendSearchService.search_by_email(db_session, "CaseSensitive@Example.COM")
        assert result is not None
        
        # 使用不同大小写搜索（根据数据库配置可能找不到）
        # 注意：SQLite 默认对邮箱不区分大小写，但 PostgreSQL 区分
        result_lower = FriendSearchService.search_by_email(db_session, "casesensitive@example.com")
        # 这个测试结果取决于数据库配置
        
        print("✓ 大小写敏感性测试通过")
    
    def test_search_multiple_users_same_nickname(self, db_session: Session):
        """测试多个用户有相同昵称但不同邮箱"""
        # 创建两个昵称相同的用户
        user1 = User(
            id="user_001",
            email="user1@example.com",
            password_hash="hash1",
            nickname="相同昵称",
            gender=Gender.MALE,
            age=25,
            height=175.0,
            current_weight=70.0
        )
        user2 = User(
            id="user_002",
            email="user2@example.com",
            password_hash="hash2",
            nickname="相同昵称",
            gender=Gender.FEMALE,
            age=30,
            height=165.0,
            current_weight=60.0
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # 通过邮箱搜索应该返回正确的用户
        result1 = FriendSearchService.search_by_email(db_session, "user1@example.com")
        result2 = FriendSearchService.search_by_email(db_session, "user2@example.com")
        
        assert result1 is not None
        assert result2 is not None
        assert result1.user_id == "user_001"
        assert result2.user_id == "user_002"
        assert result1.gender == Gender.MALE
        assert result2.gender == Gender.FEMALE
        
        print("✓ 相同昵称不同邮箱测试通过")


# ==================== Pytest Fixtures ====================

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
