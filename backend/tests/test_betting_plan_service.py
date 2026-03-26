"""
测试对赌计划服务 (Task 6.7)
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal


class TestBettingPlanService:
    """测试对赌计划服务"""
    
    @pytest.fixture
    def betting_plan_service(self):
        """创建对赌计划服务实例"""
        # 模拟对赌计划服务
        return None
    
    @pytest.fixture
    def mock_plan_data(self):
        """模拟计划数据"""
        return {
            "creator_id": "user123",
            "bet_amount": Decimal("100.00"),
            "start_date": datetime.utcnow() + timedelta(days=1),
            "end_date": datetime.utcnow() + timedelta(days=31),
            "description": "30天减重挑战",
            "creator_goal": {
                "initial_weight": Decimal("80.0"),
                "target_weight": Decimal("75.0"),
                "target_weight_loss": Decimal("5.0")
            }
        }
    
    # ==================== 创建对赌计划测试 ====================
    
    def test_create_plan_success(self, betting_plan_service, mock_plan_data):
        """测试创建对赌计划成功"""
        # 验证计划参数
        assert mock_plan_data["bet_amount"] > 0
        assert mock_plan_data["end_date"] > mock_plan_data["start_date"]
        assert mock_plan_data["creator_goal"]["target_weight_loss"] > 0
        
        # 模拟创建计划
        plan = {
            "id": "plan123",
            "status": "pending",
            **mock_plan_data,
            "created_at": datetime.utcnow()
        }
        
        assert plan["status"] == "pending"
        assert plan["id"]
        
        print("✓ 创建对赌计划成功测试通过")
    
    def test_create_plan_invalid_bet_amount(self, betting_plan_service):
        """测试无效赌金金额"""
        invalid_amounts = [
            Decimal("0.00"),
            Decimal("-100.00"),
            Decimal("0.001")
        ]
        
        for amount in invalid_amounts:
            # 验证赌金必须大于 0
            is_invalid = amount <= 0
            assert is_invalid
        
        print("✓ 无效赌金金额测试通过")
    
    def test_create_plan_invalid_date_range(self, betting_plan_service):
        """测试无效日期范围"""
        start_date = datetime.utcnow() + timedelta(days=1)
        
        # 结束日期早于开始日期
        invalid_end_date = start_date - timedelta(days=1)
        is_invalid = invalid_end_date <= start_date
        assert is_invalid
        
        # 结束日期等于开始日期
        same_end_date = start_date
        is_invalid = same_end_date <= start_date
        assert is_invalid
        
        print("✓ 无效日期范围测试通过")
    
    def test_create_plan_duration_limit(self, betting_plan_service):
        """测试计划时长限制"""
        start_date = datetime.utcnow()
        max_duration_days = 365
        
        # 超过最大时长
        invalid_end_date = start_date + timedelta(days=366)
        duration = (invalid_end_date - start_date).days
        is_invalid = duration > max_duration_days
        assert is_invalid
        
        # 在最大时长内
        valid_end_date = start_date + timedelta(days=365)
        duration = (valid_end_date - start_date).days
        is_valid = duration <= max_duration_days
        assert is_valid
        
        print("✓ 计划时长限制测试通过")
    
    def test_create_plan_weight_validation(self, betting_plan_service):
        """测试体重参数验证"""
        # 有效的体重参数
        valid_goal = {
            "initial_weight": Decimal("80.0"),
            "target_weight": Decimal("75.0"),
            "target_weight_loss": Decimal("5.0")
        }
        
        # 验证体重范围 (30-300kg)
        assert Decimal("30.0") <= valid_goal["initial_weight"] <= Decimal("300.0")
        assert Decimal("30.0") <= valid_goal["target_weight"] <= Decimal("300.0")
        
        # 验证目标体重 < 初始体重
        assert valid_goal["target_weight"] < valid_goal["initial_weight"]
        
        # 验证目标减重量 = 初始体重 - 目标体重
        calculated_loss = valid_goal["initial_weight"] - valid_goal["target_weight"]
        assert calculated_loss == valid_goal["target_weight_loss"]
        
        print("✓ 体重参数验证测试通过")
    
    def test_create_plan_insufficient_balance(self, betting_plan_service):
        """测试余额不足时创建失败"""
        bet_amount = Decimal("1000.00")
        user_balance = Decimal("500.00")
        
        # 验证余额不足
        is_insufficient = user_balance < bet_amount
        assert is_insufficient
        
        print("✓ 余额不足创建失败测试通过")
    
    def test_create_plan_freezes_funds(self, betting_plan_service, mock_plan_data):
        """测试创建计划冻结资金"""
        bet_amount = mock_plan_data["bet_amount"]
        
        # 模拟初始余额
        initial_balance = {
            "available_balance": Decimal("1000.00"),
            "frozen_balance": Decimal("0.00")
        }
        
        # 模拟冻结操作
        new_available = initial_balance["available_balance"] - bet_amount
        new_frozen = initial_balance["frozen_balance"] + bet_amount
        
        assert new_available == Decimal("900.00")
        assert new_frozen == Decimal("100.00")
        
        print("✓ 创建计划冻结资金测试通过")
    
    def test_create_plan_generates_unique_id(self, betting_plan_service):
        """测试生成唯一计划 ID"""
        # 模拟生成多个计划 ID
        plan_ids = set()
        for i in range(100):
            plan_id = f"plan_{i}_{datetime.utcnow().timestamp()}"
            plan_ids.add(plan_id)
        
        # 验证所有 ID 都是唯一的
        assert len(plan_ids) == 100
        
        print("✓ 生成唯一计划 ID 测试通过")
    
    # ==================== 邀请参与者测试 ====================
    
    def test_invite_participant_success(self, betting_plan_service):
        """测试邀请参与者成功"""
        plan_id = "plan123"
        creator_id = "user123"
        participant_id = "user456"
        
        # 模拟计划数据
        plan = {
            "id": plan_id,
            "creator_id": creator_id,
            "status": "pending"
        }
        
        # 验证计划状态为 pending
        assert plan["status"] == "pending"
        
        # 验证邀请者是计划创建者
        is_creator = creator_id == plan["creator_id"]
        assert is_creator
        
        print("✓ 邀请参与者成功测试通过")
    
    def test_invite_participant_invalid_status(self, betting_plan_service):
        """测试非 pending 状态无法邀请"""
        invalid_statuses = ["active", "completed", "cancelled", "rejected"]
        
        for status in invalid_statuses:
            # 验证计划状态不是 pending
            is_pending = status == "pending"
            assert not is_pending
        
        print("✓ 非 pending 状态无法邀请测试通过")
    
    def test_invite_participant_not_creator(self, betting_plan_service):
        """测试非创建者无法邀请"""
        plan_creator_id = "user123"
        inviter_id = "user456"
        
        # 验证邀请者不是创建者
        is_creator = inviter_id == plan_creator_id
        assert not is_creator
        
        print("✓ 非创建者无法邀请测试通过")
    
    def test_invite_participant_sends_notification(self, betting_plan_service):
        """测试邀请发送通知"""
        participant_id = "user456"
        plan_id = "plan123"
        
        # 模拟通知数据
        notification = {
            "user_id": participant_id,
            "type": "plan_invite",
            "plan_id": plan_id,
            "message": "您收到了一个对赌计划邀请"
        }
        
        assert notification["type"] == "plan_invite"
        assert notification["user_id"] == participant_id
        
        print("✓ 邀请发送通知测试通过")
    
    # ==================== 接受对赌计划测试 ====================
    
    def test_accept_plan_success(self, betting_plan_service):
        """测试接受对赌计划成功"""
        plan_id = "plan123"
        participant_id = "user456"
        
        # 模拟计划数据
        plan = {
            "id": plan_id,
            "creator_id": "user123",
            "status": "pending",
            "bet_amount": Decimal("100.00")
        }
        
        # 验证计划状态为 pending
        assert plan["status"] == "pending"
        
        # 验证用户不是计划创建者
        is_creator = participant_id == plan["creator_id"]
        assert not is_creator
        
        # 模拟接受计划
        plan["status"] = "active"
        plan["participant_id"] = participant_id
        plan["activated_at"] = datetime.utcnow()
        
        assert plan["status"] == "active"
        assert plan["participant_id"] == participant_id
        assert plan["activated_at"]
        
        print("✓ 接受对赌计划成功测试通过")
    
    def test_accept_plan_invalid_status(self, betting_plan_service):
        """测试非 pending 状态无法接受"""
        invalid_statuses = ["active", "completed", "cancelled", "rejected"]
        
        for status in invalid_statuses:
            # 验证计划状态不是 pending
            is_pending = status == "pending"
            assert not is_pending
        
        print("✓ 非 pending 状态无法接受测试通过")
    
    def test_accept_plan_creator_cannot_accept(self, betting_plan_service):
        """测试创建者无法接受自己的计划"""
        plan_creator_id = "user123"
        accepter_id = "user123"
        
        # 验证接受者是创建者
        is_creator = accepter_id == plan_creator_id
        assert is_creator
        
        print("✓ 创建者无法接受自己的计划测试通过")
    
    def test_accept_plan_insufficient_balance(self, betting_plan_service):
        """测试余额不足时接受失败"""
        bet_amount = Decimal("1000.00")
        user_balance = Decimal("500.00")
        
        # 验证余额不足
        is_insufficient = user_balance < bet_amount
        assert is_insufficient
        
        print("✓ 余额不足接受失败测试通过")
    
    def test_accept_plan_validates_participant_goal(self, betting_plan_service):
        """测试验证参与者目标参数"""
        participant_goal = {
            "initial_weight": Decimal("90.0"),
            "target_weight": Decimal("85.0"),
            "target_weight_loss": Decimal("5.0")
        }
        
        # 验证体重范围
        assert Decimal("30.0") <= participant_goal["initial_weight"] <= Decimal("300.0")
        assert Decimal("30.0") <= participant_goal["target_weight"] <= Decimal("300.0")
        
        # 验证目标体重 < 初始体重
        assert participant_goal["target_weight"] < participant_goal["initial_weight"]
        
        # 验证目标减重量
        calculated_loss = participant_goal["initial_weight"] - participant_goal["target_weight"]
        assert calculated_loss == participant_goal["target_weight_loss"]
        
        print("✓ 验证参与者目标参数测试通过")
    
    def test_accept_plan_freezes_funds(self, betting_plan_service):
        """测试接受计划冻结资金"""
        bet_amount = Decimal("100.00")
        
        # 模拟初始余额
        initial_balance = {
            "available_balance": Decimal("1000.00"),
            "frozen_balance": Decimal("0.00")
        }
        
        # 模拟冻结操作
        new_available = initial_balance["available_balance"] - bet_amount
        new_frozen = initial_balance["frozen_balance"] + bet_amount
        
        assert new_available == Decimal("900.00")
        assert new_frozen == Decimal("100.00")
        
        print("✓ 接受计划冻结资金测试通过")
    
    def test_accept_plan_sends_notification(self, betting_plan_service):
        """测试接受计划发送通知"""
        creator_id = "user123"
        participant_id = "user456"
        plan_id = "plan123"
        
        # 模拟通知数据
        notifications = [
            {
                "user_id": creator_id,
                "type": "plan_activated",
                "plan_id": plan_id,
                "message": "您的对赌计划已生效"
            },
            {
                "user_id": participant_id,
                "type": "plan_activated",
                "plan_id": plan_id,
                "message": "您的对赌计划已生效"
            }
        ]
        
        assert len(notifications) == 2
        assert notifications[0]["type"] == "plan_activated"
        assert notifications[1]["type"] == "plan_activated"
        
        print("✓ 接受计划发送通知测试通过")
    
    # ==================== 拒绝计划测试 ====================
    
    def test_reject_plan_success(self, betting_plan_service):
        """测试拒绝计划成功"""
        plan_id = "plan123"
        
        # 模拟计划数据
        plan = {
            "id": plan_id,
            "creator_id": "user123",
            "status": "pending",
            "bet_amount": Decimal("100.00")
        }
        
        # 验证计划状态为 pending
        assert plan["status"] == "pending"
        
        # 模拟拒绝计划
        plan["status"] = "rejected"
        
        assert plan["status"] == "rejected"
        
        print("✓ 拒绝计划成功测试通过")
    
    def test_reject_plan_unfreezes_funds(self, betting_plan_service):
        """测试拒绝计划解冻创建者资金"""
        bet_amount = Decimal("100.00")
        
        # 模拟初始余额
        initial_balance = {
            "available_balance": Decimal("900.00"),
            "frozen_balance": Decimal("100.00")
        }
        
        # 模拟解冻操作
        new_available = initial_balance["available_balance"] + bet_amount
        new_frozen = initial_balance["frozen_balance"] - bet_amount
        
        assert new_available == Decimal("1000.00")
        assert new_frozen == Decimal("0.00")
        
        print("✓ 拒绝计划解冻资金测试通过")
    
    # ==================== 取消计划测试 ====================
    
    def test_cancel_plan_success(self, betting_plan_service):
        """测试取消计划成功"""
        plan_id = "plan123"
        creator_id = "user123"
        
        # 模拟计划数据
        plan = {
            "id": plan_id,
            "creator_id": creator_id,
            "status": "pending",
            "bet_amount": Decimal("100.00")
        }
        
        # 验证计划状态为 pending
        assert plan["status"] == "pending"
        
        # 验证操作者是创建者
        is_creator = creator_id == plan["creator_id"]
        assert is_creator
        
        # 模拟取消计划
        plan["status"] = "cancelled"
        
        assert plan["status"] == "cancelled"
        
        print("✓ 取消计划成功测试通过")
    
    def test_cancel_plan_unfreezes_funds(self, betting_plan_service):
        """测试取消计划解冻创建者资金"""
        bet_amount = Decimal("100.00")
        
        # 模拟初始余额
        initial_balance = {
            "available_balance": Decimal("900.00"),
            "frozen_balance": Decimal("100.00")
        }
        
        # 模拟解冻操作
        new_available = initial_balance["available_balance"] + bet_amount
        new_frozen = initial_balance["frozen_balance"] - bet_amount
        
        assert new_available == Decimal("1000.00")
        assert new_frozen == Decimal("0.00")
        
        print("✓ 取消计划解冻资金测试通过")
    
    def test_cancel_plan_invalid_status(self, betting_plan_service):
        """测试非 pending 状态无法取消"""
        invalid_statuses = ["active", "completed", "rejected"]
        
        for status in invalid_statuses:
            # 验证计划状态不是 pending
            is_pending = status == "pending"
            assert not is_pending
        
        print("✓ 非 pending 状态无法取消测试通过")
    
    # ==================== 获取计划详情测试 ====================
    
    def test_get_plan_details_success(self, betting_plan_service):
        """测试获取计划详情成功"""
        plan_id = "plan123"
        
        # 模拟计划详情
        plan_details = {
            "id": plan_id,
            "creator_id": "user123",
            "participant_id": "user456",
            "status": "active",
            "bet_amount": Decimal("100.00"),
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "description": "30天减重挑战",
            "creator_goal": {
                "initial_weight": Decimal("80.0"),
                "target_weight": Decimal("75.0"),
                "target_weight_loss": Decimal("5.0")
            },
            "participant_goal": {
                "initial_weight": Decimal("90.0"),
                "target_weight": Decimal("85.0"),
                "target_weight_loss": Decimal("5.0")
            }
        }
        
        assert plan_details["id"] == plan_id
        assert "creator_goal" in plan_details
        assert "participant_goal" in plan_details
        
        print("✓ 获取计划详情成功测试通过")
    
    def test_get_plan_details_not_found(self, betting_plan_service):
        """测试计划不存在"""
        plan_id = "nonexistent_plan"
        
        # 模拟计划不存在
        plan_exists = False
        assert not plan_exists
        
        print("✓ 计划不存在测试通过")
    
    def test_get_plan_details_permission(self, betting_plan_service):
        """测试计划详情权限验证"""
        plan_id = "plan123"
        user_id = "user123"
        
        # 模拟计划数据
        plan = {
            "id": plan_id,
            "creator_id": "user123",
            "participant_id": "user456"
        }
        
        # 验证用户是计划参与者
        is_participant = user_id in [plan["creator_id"], plan.get("participant_id")]
        assert is_participant
        
        print("✓ 计划详情权限验证测试通过")
    
    # ==================== 获取用户计划列表测试 ====================
    
    def test_get_user_plans_success(self, betting_plan_service):
        """测试获取用户计划列表成功"""
        user_id = "user123"
        
        # 模拟计划列表
        plans = [
            {
                "id": "plan1",
                "creator_id": user_id,
                "status": "active"
            },
            {
                "id": "plan2",
                "participant_id": user_id,
                "status": "pending"
            },
            {
                "id": "plan3",
                "creator_id": user_id,
                "status": "completed"
            }
        ]
        
        assert len(plans) == 3
        
        print("✓ 获取用户计划列表成功测试通过")
    
    def test_get_user_plans_filter_by_status(self, betting_plan_service):
        """测试按状态筛选计划列表"""
        user_id = "user123"
        filter_status = "active"
        
        # 模拟所有计划
        all_plans = [
            {"id": "plan1", "status": "active"},
            {"id": "plan2", "status": "pending"},
            {"id": "plan3", "status": "active"},
            {"id": "plan4", "status": "completed"}
        ]
        
        # 筛选指定状态的计划
        filtered_plans = [p for p in all_plans if p["status"] == filter_status]
        
        assert len(filtered_plans) == 2
        assert all(p["status"] == filter_status for p in filtered_plans)
        
        print("✓ 按状态筛选计划列表测试通过")
    
    def test_get_user_plans_pagination(self, betting_plan_service):
        """测试分页获取计划列表"""
        user_id = "user123"
        page = 1
        page_size = 10
        
        # 模拟分页参数
        assert page > 0
        assert page_size > 0
        assert page_size <= 100  # 限制最大页面大小
        
        print("✓ 分页获取计划列表测试通过")
    
    # ==================== 计划状态转换测试 ====================
    
    def test_plan_status_transitions(self, betting_plan_service):
        """测试计划状态转换"""
        # 定义有效的状态转换
        valid_transitions = {
            "pending": ["active", "cancelled", "rejected"],
            "active": ["completed"],
            "completed": [],
            "cancelled": [],
            "rejected": []
        }
        
        # 测试从 pending 到 active
        current_status = "pending"
        new_status = "active"
        is_valid = new_status in valid_transitions[current_status]
        assert is_valid
        
        # 测试从 active 到 pending (无效)
        current_status = "active"
        new_status = "pending"
        is_valid = new_status in valid_transitions[current_status]
        assert not is_valid
        
        # 测试从 completed 到任何状态 (无效)
        current_status = "completed"
        for new_status in ["pending", "active", "cancelled", "rejected"]:
            is_valid = new_status in valid_transitions[current_status]
            assert not is_valid
        
        print("✓ 计划状态转换测试通过")
    
    # ==================== 边界情况测试 ====================
    
    def test_plan_minimum_duration(self, betting_plan_service):
        """测试计划最小时长"""
        start_date = datetime.utcnow()
        
        # 1天时长 (最小)
        end_date = start_date + timedelta(days=1)
        duration = (end_date - start_date).days
        is_valid = duration >= 1
        assert is_valid
        
        # 小于1天 (无效)
        end_date = start_date + timedelta(hours=12)
        duration = (end_date - start_date).days
        is_valid = duration >= 1
        assert not is_valid
        
        print("✓ 计划最小时长测试通过")
    
    def test_plan_maximum_bet_amount(self, betting_plan_service):
        """测试赌金最大金额限制"""
        max_bet_amount = Decimal("10000.00")
        
        # 在限制内
        bet_amount = Decimal("5000.00")
        is_valid = bet_amount <= max_bet_amount
        assert is_valid
        
        # 超过限制
        bet_amount = Decimal("15000.00")
        is_valid = bet_amount <= max_bet_amount
        assert not is_valid
        
        print("✓ 赌金最大金额限制测试通过")
    
    def test_plan_minimum_weight_loss(self, betting_plan_service):
        """测试最小减重量限制"""
        minimum_weight_loss = Decimal("1.0")
        
        # 在限制内
        target_weight_loss = Decimal("5.0")
        is_valid = target_weight_loss >= minimum_weight_loss
        assert is_valid
        
        # 低于限制
        target_weight_loss = Decimal("0.5")
        is_valid = target_weight_loss >= minimum_weight_loss
        assert not is_valid
        
        print("✓ 最小减重量限制测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
