# -*- coding: utf-8 -*-
"""
社交服务测试 (Social Service Tests)
Tests for Task 10: 实现社交服务 (SocialService)
"""
import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, Gender
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.check_in import CheckIn, ReviewStatus
from app.models.settlement import Settlement
from app.models.comment import Comment
from app.models.badge import UserBadge, BadgeType
from app.models.balance import Balance
from app.services.social_service import SocialService
from app.schemas.social import (
    LeaderboardType,
    CommentRequest,
    BadgeResponse
)
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
    users = []
    for i in range(5):
        user = User(
            id=f"user{i+1}",
            email=f"user{i+1}@test.com",
            password_hash="hashed_password",
            nickname=f"User {i+1}",
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
            age=25 + i,
            height=170.0 + i * 5,
            current_weight=70.0 + i * 5
        )
        users.append(user)
        db.add(user)
        
        # 创建余额记录
        balance = Balance(
            user_id=user.id,
            available_balance=1000.0,
            frozen_balance=0.0
        )
        db.add(balance)
    
    db.commit()
    return users


@pytest.fixture
def completed_plans(db, test_users):
    """创建已完成的测试计划"""
    plans = []
    for i in range(3):
        plan = BettingPlan(
            id=f"plan{i+1}",
            creator_id=test_users[i].id,
            participant_id=test_users[i+1].id,
            status=PlanStatus.COMPLETED,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=35),
            end_date=datetime.now() - timedelta(days=5),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0,
            participant_initial_weight=70.0,
            participant_target_weight=65.0,
            participant_target_weight_loss=5.0,
            activated_at=datetime.now() - timedelta(days=35)
        )
        plans.append(plan)
        db.add(plan)
    
    db.commit()
    return plans


class TestLeaderboards:
    """测试排行榜功能 (Task 10.1)"""
    
    def test_weight_loss_leaderboard(self, db, test_users):
        """测试减重排行榜"""
        # 为用户创建打卡记录,模拟不同的减重量
        for i, user in enumerate(test_users[:3]):
            # 创建计划
            plan = BettingPlan(
                id=f"plan_wl_{i}",
                creator_id=user.id,
                status=PlanStatus.ACTIVE,
                bet_amount=100.0,
                start_date=datetime.now() - timedelta(days=10),
                end_date=datetime.now() + timedelta(days=20),
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db.add(plan)
            db.commit()
            
            # 创建初始体重打卡
            check_in1 = CheckIn(
                id=f"checkin_wl_{i}_1",
                user_id=user.id,
                plan_id=plan.id,
                weight=80.0,
                check_in_date=date.today() - timedelta(days=10),
                review_status=ReviewStatus.APPROVED
            )
            db.add(check_in1)
            
            # 创建最新体重打卡 (不同的减重量)
            check_in2 = CheckIn(
                id=f"checkin_wl_{i}_2",
                user_id=user.id,
                plan_id=plan.id,
                weight=80.0 - (i + 1) * 2,  # user1: 78kg, user2: 76kg, user3: 74kg
                check_in_date=date.today(),
                review_status=ReviewStatus.APPROVED
            )
            db.add(check_in2)
        
        db.commit()
        
        # 获取减重排行榜
        leaderboard = SocialService.get_weight_loss_leaderboard(db, limit=10)
        
        assert len(leaderboard) == 3
        # 验证排序 (减重最多的在前)
        assert leaderboard[0].value == 6.0  # user3 减重 6kg
        assert leaderboard[1].value == 4.0  # user2 减重 4kg
        assert leaderboard[2].value == 2.0  # user1 减重 2kg
        # 验证排名
        assert leaderboard[0].rank == 1
        assert leaderboard[1].rank == 2
        assert leaderboard[2].rank == 3
    
    def test_check_in_streak_leaderboard(self, db, test_users):
        """测试连续打卡排行榜"""
        # 为用户创建不同的连续打卡记录
        for i, user in enumerate(test_users[:3]):
            plan = BettingPlan(
                id=f"plan_streak_{i}",
                creator_id=user.id,
                status=PlanStatus.ACTIVE,
                bet_amount=100.0,
                start_date=datetime.now() - timedelta(days=15),
                end_date=datetime.now() + timedelta(days=15),
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db.add(plan)
            db.commit()
            
            # 创建连续打卡记录 (不同的连续天数)
            streak_days = (i + 1) * 3  # user1: 3天, user2: 6天, user3: 9天
            for day in range(streak_days):
                check_in = CheckIn(
                    id=f"checkin_streak_{i}_{day}",
                    user_id=user.id,
                    plan_id=plan.id,
                    weight=80.0 - day * 0.1,
                    check_in_date=date.today() - timedelta(days=streak_days - day - 1),
                    review_status=ReviewStatus.APPROVED
                )
                db.add(check_in)
        
        db.commit()
        
        # 获取连续打卡排行榜
        leaderboard = SocialService.get_check_in_streak_leaderboard(db, limit=10)
        
        assert len(leaderboard) == 3
        # 验证排序 (连续天数最多的在前)
        assert leaderboard[0].value == 9.0  # user3 连续 9 天
        assert leaderboard[1].value == 6.0  # user2 连续 6 天
        assert leaderboard[2].value == 3.0  # user1 连续 3 天
    
    def test_win_rate_leaderboard(self, db, test_users):
        """测试胜率排行榜"""
        # 为前3个用户创建结算记录,模拟不同的胜率
        # user1: 5个计划, 4胜 (80%)
        # user2: 5个计划, 3胜 (60%)
        # user3: 5个计划, 5胜 (100%)
        
        for i in range(3):
            user = test_users[i]
            wins = [4, 3, 5][i]
            
            for j in range(5):
                plan = BettingPlan(
                    id=f"plan_wr_{i}_{j}",
                    creator_id=user.id,
                    participant_id=test_users[4].id,
                    status=PlanStatus.COMPLETED,
                    bet_amount=100.0,
                    start_date=datetime.now() - timedelta(days=35),
                    end_date=datetime.now() - timedelta(days=5),
                    creator_initial_weight=80.0,
                    creator_target_weight=75.0,
                    creator_target_weight_loss=5.0,
                    participant_initial_weight=70.0,
                    participant_target_weight=65.0,
                    participant_target_weight_loss=5.0
                )
                db.add(plan)
                db.commit()
                
                # 创建结算记录
                settlement = Settlement(
                    id=f"settlement_wr_{i}_{j}",
                    plan_id=plan.id,
                    creator_achieved=j < wins,  # 前wins个计划达成目标
                    participant_achieved=False,
                    creator_final_weight=75.0 if j < wins else 78.0,
                    participant_final_weight=68.0,
                    creator_weight_loss=5.0 if j < wins else 2.0,
                    participant_weight_loss=2.0,
                    creator_amount=200.0 if j < wins else 0.0,
                    participant_amount=0.0 if j < wins else 200.0,
                    platform_fee=0.0,
                    settlement_date=datetime.now()
                )
                db.add(settlement)
        
        db.commit()
        
        # 获取胜率排行榜
        leaderboard = SocialService.get_win_rate_leaderboard(db, limit=10)
        
        # user5 also has 15 completed plans as participant, so we expect 4 users
        assert len(leaderboard) >= 3
        # 验证前3名的排序 (胜率最高的在前)
        assert leaderboard[0].value == 100.0  # user3 胜率 100%
        assert leaderboard[1].value == 80.0   # user1 胜率 80%
        assert leaderboard[2].value == 60.0   # user2 胜率 60%
    
    def test_leaderboard_limit(self, db, test_users):
        """测试排行榜数量限制"""
        # 创建多个用户的打卡记录
        for i, user in enumerate(test_users):
            plan = BettingPlan(
                id=f"plan_limit_{i}",
                creator_id=user.id,
                status=PlanStatus.ACTIVE,
                bet_amount=100.0,
                start_date=datetime.now() - timedelta(days=10),
                end_date=datetime.now() + timedelta(days=20),
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db.add(plan)
            db.commit()
            
            check_in1 = CheckIn(
                id=f"checkin_limit_{i}_1",
                user_id=user.id,
                plan_id=plan.id,
                weight=80.0,
                check_in_date=date.today() - timedelta(days=5),
                review_status=ReviewStatus.APPROVED
            )
            check_in2 = CheckIn(
                id=f"checkin_limit_{i}_2",
                user_id=user.id,
                plan_id=plan.id,
                weight=75.0,
                check_in_date=date.today(),
                review_status=ReviewStatus.APPROVED
            )
            db.add(check_in1)
            db.add(check_in2)
        
        db.commit()
        
        # 测试限制返回数量
        leaderboard = SocialService.get_weight_loss_leaderboard(db, limit=3)
        
        assert len(leaderboard) == 3


class TestComments:
    """测试评论功能 (Task 10.2)"""
    
    def test_create_comment(self, db, test_users, completed_plans):
        """测试创建评论"""
        plan = completed_plans[0]
        user = test_users[0]
        
        request = CommentRequest(content="这个计划很棒!")
        
        comment = SocialService.create_comment(db, plan.id, user.id, request)
        
        assert comment.id is not None
        assert comment.plan_id == plan.id
        assert comment.user_id == user.id
        assert comment.content == "这个计划很棒!"
        assert comment.user_nickname == user.nickname
        assert comment.created_at is not None
    
    def test_create_comment_plan_not_found(self, db, test_users):
        """测试计划不存在时创建评论"""
        user = test_users[0]
        request = CommentRequest(content="测试评论")
        
        with pytest.raises(HTTPException) as exc_info:
            SocialService.create_comment(db, "nonexistent_plan", user.id, request)
        
        assert exc_info.value.status_code == 404
        assert "Plan not found" in exc_info.value.detail
    
    def test_create_comment_user_not_found(self, db, completed_plans):
        """测试用户不存在时创建评论"""
        plan = completed_plans[0]
        request = CommentRequest(content="测试评论")
        
        with pytest.raises(HTTPException) as exc_info:
            SocialService.create_comment(db, plan.id, "nonexistent_user", request)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail
    
    def test_get_comments(self, db, test_users, completed_plans):
        """测试获取评论列表"""
        plan = completed_plans[0]
        
        # 创建多条评论
        for i in range(3):
            request = CommentRequest(content=f"评论 {i+1}")
            SocialService.create_comment(db, plan.id, test_users[i].id, request)
        
        # 获取评论列表
        comments = SocialService.get_comments(db, plan.id, limit=10)
        
        assert len(comments) == 3
        # 验证按时间倒序排列
        assert comments[0].created_at >= comments[1].created_at
        assert comments[1].created_at >= comments[2].created_at
    
    def test_get_comments_with_limit(self, db, test_users, completed_plans):
        """测试限制评论数量"""
        plan = completed_plans[0]
        
        # 创建5条评论
        for i in range(5):
            request = CommentRequest(content=f"评论 {i+1}")
            SocialService.create_comment(db, plan.id, test_users[0].id, request)
        
        # 限制返回3条
        comments = SocialService.get_comments(db, plan.id, limit=3)
        
        assert len(comments) == 3
    
    def test_comment_content_validation(self, db, test_users, completed_plans):
        """测试评论内容验证"""
        plan = completed_plans[0]
        user = test_users[0]
        
        # 测试空内容
        with pytest.raises(Exception):  # Pydantic validation error
            request = CommentRequest(content="")
            SocialService.create_comment(db, plan.id, user.id, request)
        
        # 测试超长内容 (>500字符)
        with pytest.raises(Exception):  # Pydantic validation error
            request = CommentRequest(content="a" * 501)
            SocialService.create_comment(db, plan.id, user.id, request)


class TestBadges:
    """测试勋章系统 (Task 10.4)"""
    
    def test_award_first_challenge_badge(self, db, test_users):
        """测试授予"初次挑战"勋章"""
        user = test_users[0]
        
        badge = SocialService.award_badge(db, user.id, BadgeType.FIRST_CHALLENGE)
        
        assert badge.id is not None
        assert badge.user_id == user.id
        assert badge.badge_type == BadgeType.FIRST_CHALLENGE
        assert badge.badge_name == "First Challenge"
        assert badge.badge_description == "Completed your first betting plan"
        assert badge.earned_at is not None
    
    def test_award_badge_duplicate(self, db, test_users):
        """测试重复授予勋章"""
        user = test_users[0]
        
        # 第一次授予
        badge1 = SocialService.award_badge(db, user.id, BadgeType.WEEK_STREAK)
        
        # 第二次授予相同勋章
        badge2 = SocialService.award_badge(db, user.id, BadgeType.WEEK_STREAK)
        
        # 应该返回相同的勋章
        assert badge1.id == badge2.id
    
    def test_get_user_badges(self, db, test_users):
        """测试获取用户勋章列表"""
        user = test_users[0]
        
        # 授予多个勋章
        SocialService.award_badge(db, user.id, BadgeType.FIRST_CHALLENGE)
        SocialService.award_badge(db, user.id, BadgeType.WEEK_STREAK)
        SocialService.award_badge(db, user.id, BadgeType.MONTH_STREAK)
        
        # 获取勋章列表
        badges = SocialService.get_user_badges(db, user.id)
        
        assert len(badges) == 3
        # 验证按获得时间倒序排列
        assert badges[0].earned_at >= badges[1].earned_at
        assert badges[1].earned_at >= badges[2].earned_at
    
    def test_check_and_award_first_challenge(self, db, test_users):
        """测试自动检查并授予"初次挑战"勋章"""
        user = test_users[0]
        
        # 创建已完成的计划
        plan = BettingPlan(
            id="plan_badge_1",
            creator_id=user.id,
            participant_id=test_users[1].id,
            status=PlanStatus.COMPLETED,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=35),
            end_date=datetime.now() - timedelta(days=5),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db.add(plan)
        db.commit()
        
        # 检查并授予勋章
        SocialService.check_and_award_badges(db, user.id)
        
        # 验证勋章已授予
        badges = SocialService.get_user_badges(db, user.id)
        badge_types = [b.badge_type for b in badges]
        assert BadgeType.FIRST_CHALLENGE in badge_types
    
    def test_check_and_award_week_streak(self, db, test_users):
        """测试自动检查并授予"坚持一周"勋章"""
        user = test_users[0]
        
        # 创建计划
        plan = BettingPlan(
            id="plan_badge_week",
            creator_id=user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() + timedelta(days=20),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db.add(plan)
        db.commit()
        
        # 创建连续7天的打卡记录
        for day in range(7):
            check_in = CheckIn(
                id=f"checkin_badge_week_{day}",
                user_id=user.id,
                plan_id=plan.id,
                weight=80.0 - day * 0.2,
                check_in_date=date.today() - timedelta(days=6 - day),
                review_status=ReviewStatus.APPROVED
            )
            db.add(check_in)
        
        db.commit()
        
        # 检查并授予勋章
        SocialService.check_and_award_badges(db, user.id)
        
        # 验证勋章已授予
        badges = SocialService.get_user_badges(db, user.id)
        badge_types = [b.badge_type for b in badges]
        assert BadgeType.WEEK_STREAK in badge_types
    
    def test_check_and_award_month_streak(self, db, test_users):
        """测试自动检查并授予"坚持一月"勋章"""
        user = test_users[0]
        
        # 创建计划
        plan = BettingPlan(
            id="plan_badge_month",
            creator_id=user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=35),
            end_date=datetime.now() + timedelta(days=5),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db.add(plan)
        db.commit()
        
        # 创建连续30天的打卡记录
        for day in range(30):
            check_in = CheckIn(
                id=f"checkin_badge_month_{day}",
                user_id=user.id,
                plan_id=plan.id,
                weight=80.0 - day * 0.15,
                check_in_date=date.today() - timedelta(days=29 - day),
                review_status=ReviewStatus.APPROVED
            )
            db.add(check_in)
        
        db.commit()
        
        # 检查并授予勋章
        SocialService.check_and_award_badges(db, user.id)
        
        # 验证勋章已授予
        badges = SocialService.get_user_badges(db, user.id)
        badge_types = [b.badge_type for b in badges]
        assert BadgeType.MONTH_STREAK in badge_types
    
    def test_check_and_award_weight_loss_master(self, db, test_users):
        """测试自动检查并授予"减重达人"勋章"""
        user = test_users[0]
        
        # 创建计划
        plan = BettingPlan(
            id="plan_badge_wlm",
            creator_id=user.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.now() - timedelta(days=35),
            end_date=datetime.now() + timedelta(days=5),
            creator_initial_weight=80.0,
            creator_target_weight=70.0,
            creator_target_weight_loss=10.0
        )
        db.add(plan)
        db.commit()
        
        # 创建打卡记录,累计减重10kg
        check_in1 = CheckIn(
            id="checkin_wlm_1",
            user_id=user.id,
            plan_id=plan.id,
            weight=80.0,
            check_in_date=date.today() - timedelta(days=30),
            review_status=ReviewStatus.APPROVED
        )
        check_in2 = CheckIn(
            id="checkin_wlm_2",
            user_id=user.id,
            plan_id=plan.id,
            weight=70.0,
            check_in_date=date.today(),
            review_status=ReviewStatus.APPROVED
        )
        db.add(check_in1)
        db.add(check_in2)
        db.commit()
        
        # 检查并授予勋章
        SocialService.check_and_award_badges(db, user.id)
        
        # 验证勋章已授予
        badges = SocialService.get_user_badges(db, user.id)
        badge_types = [b.badge_type for b in badges]
        assert BadgeType.WEIGHT_LOSS_MASTER in badge_types
    
    def test_check_and_award_champion(self, db, test_users):
        """测试自动检查并授予"常胜将军"勋章"""
        user = test_users[0]
        
        # 创建5个已完成的计划,胜率80%
        for i in range(5):
            plan = BettingPlan(
                id=f"plan_badge_champion_{i}",
                creator_id=user.id,
                participant_id=test_users[1].id,
                status=PlanStatus.COMPLETED,
                bet_amount=100.0,
                start_date=datetime.now() - timedelta(days=35),
                end_date=datetime.now() - timedelta(days=5),
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db.add(plan)
            db.commit()
            
            # 前4个计划达成目标,最后1个未达成
            settlement = Settlement(
                id=f"settlement_champion_{i}",
                plan_id=plan.id,
                creator_achieved=i < 4,
                participant_achieved=False,
                creator_final_weight=75.0 if i < 4 else 78.0,
                participant_final_weight=68.0,
                creator_weight_loss=5.0 if i < 4 else 2.0,
                participant_weight_loss=2.0,
                creator_amount=200.0 if i < 4 else 0.0,
                participant_amount=0.0,
                platform_fee=0.0,
                settlement_date=datetime.now()
            )
            db.add(settlement)
        
        db.commit()
        
        # 检查并授予勋章
        SocialService.check_and_award_badges(db, user.id)
        
        # 验证勋章已授予
        badges = SocialService.get_user_badges(db, user.id)
        badge_types = [b.badge_type for b in badges]
        assert BadgeType.CHAMPION in badge_types


class TestCaching:
    """测试缓存功能"""
    
    def test_leaderboard_caching(self, db, test_users):
        """测试排行榜缓存"""
        # 创建打卡记录
        for i, user in enumerate(test_users[:2]):
            plan = BettingPlan(
                id=f"plan_cache_{i}",
                creator_id=user.id,
                status=PlanStatus.ACTIVE,
                bet_amount=100.0,
                start_date=datetime.now() - timedelta(days=10),
                end_date=datetime.now() + timedelta(days=20),
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db.add(plan)
            db.commit()
            
            check_in1 = CheckIn(
                id=f"checkin_cache_{i}_1",
                user_id=user.id,
                plan_id=plan.id,
                weight=80.0,
                check_in_date=date.today() - timedelta(days=5),
                review_status=ReviewStatus.APPROVED
            )
            check_in2 = CheckIn(
                id=f"checkin_cache_{i}_2",
                user_id=user.id,
                plan_id=plan.id,
                weight=75.0,
                check_in_date=date.today(),
                review_status=ReviewStatus.APPROVED
            )
            db.add(check_in1)
            db.add(check_in2)
        
        db.commit()
        
        # 第一次调用 (应该从数据库获取)
        leaderboard1 = SocialService.get_weight_loss_leaderboard(db, limit=10)
        
        # 第二次调用 (应该从缓存获取)
        leaderboard2 = SocialService.get_weight_loss_leaderboard(db, limit=10)
        
        # 验证结果一致
        assert len(leaderboard1) == len(leaderboard2)
        assert leaderboard1[0].user_id == leaderboard2[0].user_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
