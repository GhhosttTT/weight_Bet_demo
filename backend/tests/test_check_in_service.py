# -*- coding: utf-8 -*-
"""
打卡服务测试
"""
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.check_in import CheckIn, ReviewStatus
from app.models.balance import Balance
from app.services.check_in_service import CheckInService
from app.schemas.check_in import CreateCheckInRequest, ReviewCheckInRequest
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
def test_users(db):
    """创建测试用户"""
    user1 = User(
        id="user1",
        email="user1@test.com",
        password_hash="hashed_password",
        nickname="User 1",
        gender="male",
        age=25,
        height=175.0,
        current_weight=80.0
    )
    user2 = User(
        id="user2",
        email="user2@test.com",
        password_hash="hashed_password",
        nickname="User 2",
        gender="female",
        age=28,
        height=165.0,
        current_weight=70.0
    )
    db.add(user1)
    db.add(user2)

    
    # 创建余额记录
    balance1 = Balance(user_id="user1", available_balance=1000.0, frozen_balance=0.0)
    balance2 = Balance(user_id="user2", available_balance=1000.0, frozen_balance=0.0)
    db.add(balance1)
    db.add(balance2)
    
    db.commit()
    return user1, user2


@pytest.fixture
def active_plan(db, test_users):
    """创建激活的测试计划"""
    plan = BettingPlan(
        id="plan1",
        creator_id="user1",
        participant_id="user2",
        status=PlanStatus.ACTIVE,
        bet_amount=100.0,
        start_date=datetime.now() - timedelta(days=5),
        end_date=datetime.now() + timedelta(days=25),
        creator_initial_weight=80.0,
        creator_target_weight=75.0,
        creator_target_weight_loss=5.0,
        participant_initial_weight=70.0,
        participant_target_weight=65.0,
        participant_target_weight_loss=5.0,
        activated_at=datetime.now() - timedelta(days=5)
    )
    db.add(plan)
    db.commit()
    return plan


class TestCreateCheckIn:
    """测试创建打卡记录"""
    
    def test_create_check_in_success(self, db, active_plan):
        """测试成功创建打卡记录"""
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today(),
            note="感觉很好"
        )
        
        result = CheckInService.create_check_in(db, "user1", request)
        
        assert result.user_id == "user1"
        assert result.plan_id == "plan1"
        assert result.weight == 79.0
        assert result.review_status == ReviewStatus.APPROVED
    
    def test_create_check_in_with_photo(self, db, active_plan):
        """测试创建带照片的打卡记录"""
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today(),
            photo_url="https://example.com/photo.jpg"
        )
        
        result = CheckInService.create_check_in(db, "user1", request)
        
        assert result.photo_url == "https://example.com/photo.jpg"
    
    def test_create_check_in_plan_not_found(self, db, test_users):
        """测试计划不存在"""
        request = CreateCheckInRequest(
            plan_id="nonexistent",
            weight=79.0,
            check_in_date=date.today()
        )
        
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.create_check_in(db, "user1", request)
        
        assert exc_info.value.status_code == 404
        assert "计划不存在" in exc_info.value.detail
    
    def test_create_check_in_not_participant(self, db, active_plan):
        """测试非参与者无法打卡"""
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        
        # 创建第三个用户
        user3 = User(
            id="user3",
            email="user3@test.com",
            password_hash="hashed_password",
            nickname="User 3",
            gender="male",
            age=30,
            height=180.0,
            current_weight=85.0
        )
        db.add(user3)
        db.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.create_check_in(db, "user3", request)
        
        assert exc_info.value.status_code == 403
        assert "不是该计划的参与者" in exc_info.value.detail
    
    def test_create_check_in_plan_not_active(self, db, test_users):
        """测试计划未激活无法打卡"""
        # 创建未激活的计划
        plan = BettingPlan(
            id="plan2",
            creator_id="user1",
            participant_id=None,
            status=PlanStatus.PENDING,
            bet_amount=100.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db.add(plan)
        db.commit()
        
        request = CreateCheckInRequest(
            plan_id="plan2",
            weight=79.0,
            check_in_date=date.today()
        )
        
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.create_check_in(db, "user1", request)
        
        assert exc_info.value.status_code == 400
        assert "计划未激活" in exc_info.value.detail
    
    def test_create_check_in_date_out_of_range(self, db, active_plan):
        """测试打卡日期超出计划范围"""
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today() + timedelta(days=100)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.create_check_in(db, "user1", request)
        
        assert exc_info.value.status_code == 400
        assert "打卡日期不在计划期间内" in exc_info.value.detail
    
    def test_create_check_in_duplicate(self, db, active_plan):
        """测试重复打卡"""
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        
        # 第一次打卡
        CheckInService.create_check_in(db, "user1", request)
        
        # 第二次打卡应该失败
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.create_check_in(db, "user1", request)
        
        assert exc_info.value.status_code == 400
        assert "今日已打卡" in exc_info.value.detail
    
    def test_create_check_in_abnormal_weight_change(self, db, active_plan):
        """测试异常体重变化标记为待审核"""
        # 第一次打卡
        request1 = CreateCheckInRequest(
            plan_id="plan1",
            weight=80.0,
            check_in_date=date.today() - timedelta(days=1)
        )
        CheckInService.create_check_in(db, "user1", request1)
        
        # 第二次打卡,体重变化超过 2kg/天
        request2 = CreateCheckInRequest(
            plan_id="plan1",
            weight=77.0,  # 1天减重3kg
            check_in_date=date.today()
        )
        result = CheckInService.create_check_in(db, "user1", request2)
        
        assert result.review_status == ReviewStatus.PENDING


class TestUploadPhoto:
    """测试上传照片"""
    
    def test_upload_photo_success(self, db, active_plan):
        """测试成功上传照片"""
        # 先创建打卡记录
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        check_in = CheckInService.create_check_in(db, "user1", request)
        
        # 上传照片
        photo_url = "https://example.com/photo.jpg"
        result = CheckInService.upload_photo(db, "user1", check_in.id, photo_url)
        
        assert result.photo_url == photo_url
    
    def test_upload_photo_not_found(self, db, test_users):
        """测试打卡记录不存在"""
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.upload_photo(db, "user1", "nonexistent", "https://example.com/photo.jpg")
        
        assert exc_info.value.status_code == 404
    
    def test_upload_photo_no_permission(self, db, active_plan):
        """测试无权限上传照片"""
        # user1 创建打卡记录
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        check_in = CheckInService.create_check_in(db, "user1", request)
        
        # user2 尝试上传照片
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.upload_photo(db, "user2", check_in.id, "https://example.com/photo.jpg")
        
        assert exc_info.value.status_code == 403


class TestReviewCheckIn:
    """测试审核打卡记录"""
    
    def test_review_check_in_success(self, db, active_plan):
        """测试成功审核打卡记录"""
        # user1 创建打卡记录
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        check_in = CheckInService.create_check_in(db, "user1", request)
        
        # user2 审核
        review_request = ReviewCheckInRequest(
            review_status=ReviewStatus.APPROVED,
            review_comment="看起来不错"
        )
        result = CheckInService.review_check_in(db, check_in.id, "user2", review_request)
        
        assert result.review_status == ReviewStatus.APPROVED
        assert result.reviewer_id == "user2"
        assert result.review_comment == "看起来不错"
    
    def test_review_check_in_reject(self, db, active_plan):
        """测试拒绝打卡记录"""
        # user1 创建打卡记录
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        check_in = CheckInService.create_check_in(db, "user1", request)
        
        # user2 拒绝
        review_request = ReviewCheckInRequest(
            review_status=ReviewStatus.REJECTED,
            review_comment="数据有问题"
        )
        result = CheckInService.review_check_in(db, check_in.id, "user2", review_request)
        
        assert result.review_status == ReviewStatus.REJECTED
    
    def test_review_check_in_no_permission(self, db, active_plan):
        """测试无权限审核"""
        # user1 创建打卡记录
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today()
        )
        check_in = CheckInService.create_check_in(db, "user1", request)
        
        # 创建第三个用户
        user3 = User(
            id="user3",
            email="user3@test.com",
            password_hash="hashed_password",
            nickname="User 3",
            gender="male",
            age=30,
            height=180.0,
            current_weight=85.0
        )
        db.add(user3)
        db.commit()
        
        # user3 尝试审核
        review_request = ReviewCheckInRequest(
            review_status=ReviewStatus.APPROVED
        )
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.review_check_in(db, check_in.id, "user3", review_request)
        
        assert exc_info.value.status_code == 403


class TestGetCheckInHistory:
    """测试获取打卡历史"""
    
    def test_get_check_in_history(self, db, active_plan):
        """测试获取打卡历史"""
        # 创建多条打卡记录
        for i in range(5):
            request = CreateCheckInRequest(
                plan_id="plan1",
                weight=80.0 - i * 0.5,
                check_in_date=date.today() - timedelta(days=4-i)
            )
            CheckInService.create_check_in(db, "user1", request)
        
        # 获取历史记录
        history = CheckInService.get_check_in_history(db, "plan1", "user1")
        
        assert len(history) == 5
        # 应该按日期倒序排列
        assert history[0].check_in_date > history[-1].check_in_date
    
    def test_get_check_in_history_with_limit(self, db, active_plan):
        """测试限制返回数量"""
        # 创建多条打卡记录 (只在计划期间内)
        for i in range(5):
            request = CreateCheckInRequest(
                plan_id="plan1",
                weight=80.0 - i * 0.5,
                check_in_date=date.today() - timedelta(days=4-i)  # 从4天前到今天
            )
            CheckInService.create_check_in(db, "user1", request)
        
        # 限制返回 3 条
        history = CheckInService.get_check_in_history(db, "plan1", "user1", limit=3)
        
        assert len(history) == 3


class TestGetProgress:
    """测试计算进度统计"""
    
    def test_get_progress_no_check_ins(self, db, active_plan):
        """测试没有打卡记录时的进度"""
        progress = CheckInService.get_progress(db, "plan1", "user1")
        
        assert progress.current_weight == 80.0
        assert progress.initial_weight == 80.0
        assert progress.target_weight == 75.0
        assert progress.weight_loss == 0.0
        assert progress.progress_percentage == 0.0
        assert progress.check_in_count == 0
    
    def test_get_progress_with_check_ins(self, db, active_plan):
        """测试有打卡记录时的进度"""
        # 创建打卡记录
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=77.5,  # 减重 2.5kg
            check_in_date=date.today()
        )
        CheckInService.create_check_in(db, "user1", request)
        
        progress = CheckInService.get_progress(db, "plan1", "user1")
        
        assert progress.current_weight == 77.5
        assert progress.weight_loss == 2.5
        assert progress.target_weight_loss == 5.0
        assert progress.progress_percentage == 50.0
        assert progress.check_in_count == 1
    
    def test_get_progress_over_100_percent(self, db, active_plan):
        """测试进度超过 100% 时限制为 100"""
        # 创建打卡记录,减重超过目标
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=73.0,  # 减重 7kg,超过目标 5kg
            check_in_date=date.today()
        )
        CheckInService.create_check_in(db, "user1", request)
        
        progress = CheckInService.get_progress(db, "plan1", "user1")
        
        assert progress.progress_percentage == 100.0
    
    def test_get_progress_negative_weight_loss(self, db, active_plan):
        """测试体重增加时进度为 0"""
        # 创建打卡记录,体重增加
        request = CreateCheckInRequest(
            plan_id="plan1",
            weight=82.0,  # 体重增加 2kg
            check_in_date=date.today()
        )
        CheckInService.create_check_in(db, "user1", request)
        
        progress = CheckInService.get_progress(db, "plan1", "user1")
        
        assert progress.progress_percentage == 0.0
    
    def test_get_progress_not_participant(self, db, active_plan):
        """测试非参与者无法获取进度"""
        # 创建第三个用户
        user3 = User(
            id="user3",
            email="user3@test.com",
            password_hash="hashed_password",
            nickname="User 3",
            gender="male",
            age=30,
            height=180.0,
            current_weight=85.0
        )
        db.add(user3)
        db.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            CheckInService.get_progress(db, "plan1", "user3")
        
        assert exc_info.value.status_code == 403


class TestGetLatestWeight:
    """测试获取最新体重"""
    
    def test_get_latest_weight_no_check_ins(self, db, active_plan):
        """测试没有打卡记录时返回 None"""
        weight = CheckInService.get_latest_weight(db, "user1", "plan1")
        
        assert weight is None
    
    def test_get_latest_weight_with_check_ins(self, db, active_plan):
        """测试有打卡记录时返回最新体重"""
        # 创建多条打卡记录
        for i in range(3):
            request = CreateCheckInRequest(
                plan_id="plan1",
                weight=80.0 - i,
                check_in_date=date.today() - timedelta(days=2-i)
            )
            CheckInService.create_check_in(db, "user1", request)
        
        weight = CheckInService.get_latest_weight(db, "user1", "plan1")
        
        assert weight == 78.0  # 最新的体重
    
    def test_get_latest_weight_only_approved(self, db, active_plan):
        """测试只返回已审核通过的打卡记录"""
        # 创建已审核的打卡记录
        request1 = CreateCheckInRequest(
            plan_id="plan1",
            weight=79.0,
            check_in_date=date.today() - timedelta(days=1)
        )
        CheckInService.create_check_in(db, "user1", request1)
        
        # 创建待审核的打卡记录
        request2 = CreateCheckInRequest(
            plan_id="plan1",
            weight=77.0,
            check_in_date=date.today()
        )
        check_in = CheckInService.create_check_in(db, "user1", request2)
        
        # 手动设置为待审核
        db_check_in = db.query(CheckIn).filter(CheckIn.id == check_in.id).first()
        db_check_in.review_status = ReviewStatus.PENDING
        db.commit()
        
        weight = CheckInService.get_latest_weight(db, "user1", "plan1")
        
        # 应该返回已审核的 79.0,而不是待审核的 77.0
        assert weight == 79.0
