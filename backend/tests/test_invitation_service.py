"""
测试邀请服务 (Task 2.3, 2.4, 2.5)
"""
import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.invitation_service import InvitationService
from app.models.user import User, Gender
from app.models.betting_plan import BettingPlan, PlanStatus
from app.models.invitation import Invitation, InvitationStatus


class TestInvitationServiceCreate:
    """测试邀请创建功能 (Task 2.3)"""
    
    def test_create_invitation_success(self, db_session: Session, test_users, test_plan):
        """测试成功创建邀请"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请
        invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 验证邀请对象
        assert invitation is not None
        assert invitation.id is not None
        assert invitation.plan_id == plan.id
        assert invitation.inviter_id == creator.id
        assert invitation.invitee_email == invitee.email
        assert invitation.invitee_id == invitee.id
        assert invitation.status == InvitationStatus.PENDING
        assert invitation.sent_at is not None
        assert invitation.viewed_at is None
        assert invitation.responded_at is None
        
        print("✓ 成功创建邀请测试通过")
    
    def test_create_invitation_plan_not_found(self, db_session: Session, test_users):
        """测试计划不存在"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.create_invitation(
                db=db_session,
                plan_id="nonexistent_plan_id",
                inviter_id=creator.id,
                invitee_email=invitee.email
            )
        
        assert exc_info.value.status_code == 404
        assert "计划不存在" in exc_info.value.detail
        
        print("✓ 计划不存在测试通过")
    
    def test_create_invitation_not_creator(self, db_session: Session, test_users, test_plan):
        """测试非创建者尝试邀请"""
        invitee = test_users["invitee"]
        other_user = test_users["other"]
        plan = test_plan
        
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.create_invitation(
                db=db_session,
                plan_id=plan.id,
                inviter_id=other_user.id,  # 不是创建者
                invitee_email=invitee.email
            )
        
        assert exc_info.value.status_code == 403
        assert "只有创建者可以邀请好友" in exc_info.value.detail
        
        print("✓ 非创建者邀请测试通过")
    
    def test_create_invitation_plan_not_pending(self, db_session: Session, test_users):
        """测试计划状态不是 PENDING"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        
        # 创建一个 ACTIVE 状态的计划
        active_plan = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.ACTIVE,
            bet_amount=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db_session.add(active_plan)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.create_invitation(
                db=db_session,
                plan_id=active_plan.id,
                inviter_id=creator.id,
                invitee_email=invitee.email
            )
        
        assert exc_info.value.status_code == 400
        assert "计划状态不允许邀请" in exc_info.value.detail
        
        print("✓ 计划状态不是 PENDING 测试通过")
    
    def test_create_invitation_invalid_email_format(self, db_session: Session, test_users, test_plan):
        """测试无效邮箱格式"""
        creator = test_users["creator"]
        plan = test_plan
        
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(HTTPException) as exc_info:
                InvitationService.create_invitation(
                    db=db_session,
                    plan_id=plan.id,
                    inviter_id=creator.id,
                    invitee_email=email
                )
            
            assert exc_info.value.status_code == 400
            assert "邮箱格式无效" in exc_info.value.detail
        
        print("✓ 无效邮箱格式测试通过")
    
    def test_create_invitation_duplicate(self, db_session: Session, test_users, test_plan):
        """测试重复邀请"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建第一个邀请
        InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 尝试创建第二个邀请
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.create_invitation(
                db=db_session,
                plan_id=plan.id,
                inviter_id=creator.id,
                invitee_email=invitee.email
            )
        
        assert exc_info.value.status_code == 409
        assert "该计划已发送邀请" in exc_info.value.detail
        
        print("✓ 重复邀请测试通过")
    
    def test_create_invitation_user_not_found(self, db_session: Session, test_users, test_plan):
        """测试被邀请用户不存在"""
        creator = test_users["creator"]
        plan = test_plan
        
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.create_invitation(
                db=db_session,
                plan_id=plan.id,
                inviter_id=creator.id,
                invitee_email="nonexistent@example.com"
            )
        
        assert exc_info.value.status_code == 404
        assert "用户不存在" in exc_info.value.detail
        
        print("✓ 用户不存在测试通过")
    
    def test_create_invitation_invite_self(self, db_session: Session, test_users, test_plan):
        """测试邀请自己"""
        creator = test_users["creator"]
        plan = test_plan
        
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.create_invitation(
                db=db_session,
                plan_id=plan.id,
                inviter_id=creator.id,
                invitee_email=creator.email
            )
        
        assert exc_info.value.status_code == 400
        assert "不能邀请自己" in exc_info.value.detail
        
        print("✓ 邀请自己测试通过")


class TestInvitationServiceEdgeCases:
    """测试邀请服务边界情况 (Task 2.5 补充)"""
    
    def test_multiple_invitations_different_plans(self, db_session: Session, test_users):
        """测试同一用户可以为不同计划发送多个邀请"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        
        # 创建两个不同的计划
        plan1 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.PENDING,
            bet_amount=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        plan2 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.PENDING,
            bet_amount=200.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=60),
            creator_initial_weight=80.0,
            creator_target_weight=70.0,
            creator_target_weight_loss=10.0
        )
        db_session.add(plan1)
        db_session.add(plan2)
        db_session.commit()
        
        # 为两个计划分别创建邀请
        invitation1 = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan1.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        invitation2 = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan2.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 验证两个邀请都成功创建
        assert invitation1.id != invitation2.id
        assert invitation1.plan_id == plan1.id
        assert invitation2.plan_id == plan2.id
        
        print("✓ 多个计划邀请测试通过")
    
    def test_invitation_with_different_invitees(self, db_session: Session, test_users):
        """测试同一创建者可以邀请不同的用户到不同计划"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        other = test_users["other"]
        
        # 创建两个计划
        plan1 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.PENDING,
            bet_amount=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        plan2 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.PENDING,
            bet_amount=150.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=45),
            creator_initial_weight=80.0,
            creator_target_weight=72.0,
            creator_target_weight_loss=8.0
        )
        db_session.add(plan1)
        db_session.add(plan2)
        db_session.commit()
        
        # 邀请不同的用户
        invitation1 = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan1.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        invitation2 = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan2.id,
            inviter_id=creator.id,
            invitee_email=other.email
        )
        
        # 验证邀请创建成功且邀请对象不同
        assert invitation1.invitee_id == invitee.id
        assert invitation2.invitee_id == other.id
        
        print("✓ 邀请不同用户测试通过")
    
    def test_invitation_status_transitions(self, db_session: Session, test_users, test_plan):
        """测试邀请状态转换的完整流程"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请 - 初始状态为 PENDING
        invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        assert invitation.status == InvitationStatus.PENDING
        
        # 转换到 VIEWED
        invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.VIEWED,
            response_time=datetime.utcnow()
        )
        assert invitation.status == InvitationStatus.VIEWED
        
        # 转换到 ACCEPTED
        invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.ACCEPTED,
            response_time=datetime.utcnow()
        )
        assert invitation.status == InvitationStatus.ACCEPTED
        
        print("✓ 邀请状态转换测试通过")
    
    def test_get_user_invitations_empty(self, db_session: Session, test_users):
        """测试获取没有邀请的用户的邀请列表"""
        other = test_users["other"]
        
        # 查询没有邀请的用户
        invitations = InvitationService.get_user_invitations(
            db=db_session,
            user_id=other.id
        )
        
        assert len(invitations) == 0
        
        print("✓ 空邀请列表测试通过")


class TestInvitationServiceQuery:
    """测试邀请查询功能 (Task 2.4)"""
    
    def test_get_invitation_by_plan(self, db_session: Session, test_users, test_plan):
        """测试根据计划 ID 获取邀请"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请
        created_invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 查询邀请
        invitation = InvitationService.get_invitation_by_plan(
            db=db_session,
            plan_id=plan.id
        )
        
        assert invitation is not None
        assert invitation.id == created_invitation.id
        assert invitation.plan_id == plan.id
        
        print("✓ 根据计划 ID 获取邀请测试通过")
    
    def test_get_invitation_by_plan_not_found(self, db_session: Session):
        """测试计划没有邀请"""
        invitation = InvitationService.get_invitation_by_plan(
            db=db_session,
            plan_id="nonexistent_plan_id"
        )
        
        assert invitation is None
        
        print("✓ 计划没有邀请测试通过")
    
    def test_get_user_invitations(self, db_session: Session, test_users):
        """测试获取用户的邀请列表"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        
        # 创建多个计划和邀请
        plans = []
        for i in range(3):
            plan = BettingPlan(
                id=str(uuid.uuid4()),
                creator_id=creator.id,
                status=PlanStatus.PENDING,
                bet_amount=100.0 + i * 10,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                creator_initial_weight=80.0,
                creator_target_weight=75.0,
                creator_target_weight_loss=5.0
            )
            db_session.add(plan)
            plans.append(plan)
        
        db_session.commit()
        
        # 创建邀请
        for plan in plans:
            InvitationService.create_invitation(
                db=db_session,
                plan_id=plan.id,
                inviter_id=creator.id,
                invitee_email=invitee.email
            )
        
        # 查询用户的邀请列表
        invitations = InvitationService.get_user_invitations(
            db=db_session,
            user_id=invitee.id
        )
        
        assert len(invitations) == 3
        assert all(inv.invitee_id == invitee.id for inv in invitations)
        
        print("✓ 获取用户邀请列表测试通过")
    
    def test_get_user_invitations_with_status_filter(self, db_session: Session, test_users):
        """测试带状态筛选的邀请列表"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        
        # 创建两个计划
        plan1 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.PENDING,
            bet_amount=100.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        plan2 = BettingPlan(
            id=str(uuid.uuid4()),
            creator_id=creator.id,
            status=PlanStatus.PENDING,
            bet_amount=200.0,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            creator_initial_weight=80.0,
            creator_target_weight=75.0,
            creator_target_weight_loss=5.0
        )
        db_session.add(plan1)
        db_session.add(plan2)
        db_session.commit()
        
        # 创建邀请
        inv1 = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan1.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        inv2 = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan2.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 更新一个邀请的状态为 VIEWED
        InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=inv1.id,
            new_status=InvitationStatus.VIEWED,
            response_time=datetime.utcnow()
        )
        
        # 查询 PENDING 状态的邀请
        pending_invitations = InvitationService.get_user_invitations(
            db=db_session,
            user_id=invitee.id,
            status=InvitationStatus.PENDING
        )
        
        assert len(pending_invitations) == 1
        assert pending_invitations[0].id == inv2.id
        
        # 查询 VIEWED 状态的邀请
        viewed_invitations = InvitationService.get_user_invitations(
            db=db_session,
            user_id=invitee.id,
            status=InvitationStatus.VIEWED
        )
        
        assert len(viewed_invitations) == 1
        assert viewed_invitations[0].id == inv1.id
        
        print("✓ 带状态筛选的邀请列表测试通过")
    
    def test_update_invitation_status_to_viewed(self, db_session: Session, test_users, test_plan):
        """测试更新邀请状态为 VIEWED"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请
        invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 更新状态为 VIEWED
        response_time = datetime.utcnow()
        updated_invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.VIEWED,
            response_time=response_time
        )
        
        assert updated_invitation.status == InvitationStatus.VIEWED
        assert updated_invitation.viewed_at is not None
        assert updated_invitation.responded_at is None
        
        print("✓ 更新邀请状态为 VIEWED 测试通过")
    
    def test_update_invitation_status_to_accepted(self, db_session: Session, test_users, test_plan):
        """测试更新邀请状态为 ACCEPTED"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请
        invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 更新状态为 ACCEPTED
        response_time = datetime.utcnow()
        updated_invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.ACCEPTED,
            response_time=response_time
        )
        
        assert updated_invitation.status == InvitationStatus.ACCEPTED
        assert updated_invitation.responded_at is not None
        
        print("✓ 更新邀请状态为 ACCEPTED 测试通过")
    
    def test_update_invitation_status_to_rejected(self, db_session: Session, test_users, test_plan):
        """测试更新邀请状态为 REJECTED"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请
        invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 更新状态为 REJECTED
        response_time = datetime.utcnow()
        updated_invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.REJECTED,
            response_time=response_time
        )
        
        assert updated_invitation.status == InvitationStatus.REJECTED
        assert updated_invitation.responded_at is not None
        
        print("✓ 更新邀请状态为 REJECTED 测试通过")
    
    def test_update_invitation_status_not_found(self, db_session: Session):
        """测试更新不存在的邀请"""
        with pytest.raises(HTTPException) as exc_info:
            InvitationService.update_invitation_status(
                db=db_session,
                invitation_id="nonexistent_invitation_id",
                new_status=InvitationStatus.VIEWED,
                response_time=datetime.utcnow()
            )
        
        assert exc_info.value.status_code == 404
        assert "邀请不存在" in exc_info.value.detail
        
        print("✓ 更新不存在的邀请测试通过")
    
    def test_invitation_timestamps_ordering(self, db_session: Session, test_users, test_plan):
        """测试邀请时间戳的顺序正确性"""
        creator = test_users["creator"]
        invitee = test_users["invitee"]
        plan = test_plan
        
        # 创建邀请
        invitation = InvitationService.create_invitation(
            db=db_session,
            plan_id=plan.id,
            inviter_id=creator.id,
            invitee_email=invitee.email
        )
        
        # 验证 sent_at 已设置
        assert invitation.sent_at is not None
        sent_time = invitation.sent_at
        
        # 标记为已查看
        import time
        time.sleep(0.01)  # 确保时间戳不同
        viewed_time = datetime.utcnow()
        invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.VIEWED,
            response_time=viewed_time
        )
        
        # 验证 viewed_at 晚于 sent_at
        assert invitation.viewed_at is not None
        assert invitation.viewed_at >= sent_time
        
        # 接受邀请
        time.sleep(0.01)
        responded_time = datetime.utcnow()
        invitation = InvitationService.update_invitation_status(
            db=db_session,
            invitation_id=invitation.id,
            new_status=InvitationStatus.ACCEPTED,
            response_time=responded_time
        )
        
        # 验证 responded_at 晚于 viewed_at
        assert invitation.responded_at is not None
        assert invitation.responded_at >= invitation.viewed_at
        
        print("✓ 邀请时间戳顺序测试通过")


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


@pytest.fixture
def test_users(db_session: Session):
    """创建测试用户"""
    creator = User(
        id=str(uuid.uuid4()),
        email="creator@example.com",
        password_hash="hashed_password",
        nickname="创建者",
        gender=Gender.MALE,
        age=30,
        height=175.0,
        current_weight=80.0
    )
    
    invitee = User(
        id=str(uuid.uuid4()),
        email="invitee@example.com",
        password_hash="hashed_password",
        nickname="被邀请者",
        gender=Gender.FEMALE,
        age=25,
        height=165.0,
        current_weight=60.0
    )
    
    other = User(
        id=str(uuid.uuid4()),
        email="other@example.com",
        password_hash="hashed_password",
        nickname="其他用户",
        gender=Gender.OTHER,
        age=28,
        height=170.0,
        current_weight=70.0
    )
    
    db_session.add(creator)
    db_session.add(invitee)
    db_session.add(other)
    db_session.commit()
    
    return {
        "creator": creator,
        "invitee": invitee,
        "other": other
    }


@pytest.fixture
def test_plan(db_session: Session, test_users):
    """创建测试计划"""
    creator = test_users["creator"]
    
    plan = BettingPlan(
        id=str(uuid.uuid4()),
        creator_id=creator.id,
        status=PlanStatus.PENDING,
        bet_amount=100.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        creator_initial_weight=80.0,
        creator_target_weight=75.0,
        creator_target_weight_loss=5.0
    )
    
    db_session.add(plan)
    db_session.commit()
    
    return plan
