"""
测试 betting_plans 表的扩展字段
验证 Task 1.2 的实现: 扩展 betting_plans 表
- 添加 abandoned_by, abandoned_at, expiry_checked_at 字段
- 添加 expired 状态到 plan_status 枚举
- 添加外键约束
"""
import pytest
from app.models.betting_plan import BettingPlan, PlanStatus


class TestBettingPlanExtensions:
    """测试 betting_plans 表的扩展字段 (Task 1.2)"""
    
    def test_plan_status_includes_expired(self):
        """验证 PlanStatus 枚举包含 expired 状态 (需求 3.1, 3.6)"""
        # 验证枚举值存在
        assert hasattr(PlanStatus, 'EXPIRED'), "PlanStatus 应该有 EXPIRED 状态"
        assert PlanStatus.EXPIRED.value == 'expired', "EXPIRED 状态的值应该是 'expired'"
        
        # 验证所有必需的状态
        expected_statuses = {'pending', 'active', 'completed', 'cancelled', 'rejected', 'expired'}
        actual_statuses = {status.value for status in PlanStatus}
        assert expected_statuses == actual_statuses, f"PlanStatus 应该包含所有状态: {expected_statuses}"
        
        print("✓ PlanStatus 枚举包含 expired 状态")
    
    def test_betting_plan_model_has_abandoned_by_field(self):
        """验证 BettingPlan 模型有 abandoned_by 字段 (需求 6.2)"""
        assert hasattr(BettingPlan, 'abandoned_by'), "BettingPlan 模型应该有 abandoned_by 属性"
        
        # 验证字段类型和属性
        column = BettingPlan.abandoned_by.property.columns[0]
        assert column.type.__class__.__name__ == 'String', "abandoned_by 应该是 String 类型"
        assert column.nullable is True, "abandoned_by 应该允许为空"
        
        # 验证外键约束
        assert len(column.foreign_keys) > 0, "abandoned_by 应该有外键约束"
        fk = list(column.foreign_keys)[0]
        assert 'users' in str(fk.target_fullname), "abandoned_by 应该引用 users 表"
        
        print("✓ BettingPlan 模型有 abandoned_by 字段并有外键约束")
    
    def test_betting_plan_model_has_abandoned_at_field(self):
        """验证 BettingPlan 模型有 abandoned_at 字段 (需求 6.2)"""
        assert hasattr(BettingPlan, 'abandoned_at'), "BettingPlan 模型应该有 abandoned_at 属性"
        
        # 验证字段类型
        column = BettingPlan.abandoned_at.property.columns[0]
        assert column.type.__class__.__name__ == 'DateTime', "abandoned_at 应该是 DateTime 类型"
        assert column.nullable is True, "abandoned_at 应该允许为空"
        
        print("✓ BettingPlan 模型有 abandoned_at 字段")
    
    def test_betting_plan_model_has_expiry_checked_at_field(self):
        """验证 BettingPlan 模型有 expiry_checked_at 字段 (需求 3.6)"""
        assert hasattr(BettingPlan, 'expiry_checked_at'), "BettingPlan 模型应该有 expiry_checked_at 属性"
        
        # 验证字段类型
        column = BettingPlan.expiry_checked_at.property.columns[0]
        assert column.type.__class__.__name__ == 'DateTime', "expiry_checked_at 应该是 DateTime 类型"
        assert column.nullable is True, "expiry_checked_at 应该允许为空"
        
        print("✓ BettingPlan 模型有 expiry_checked_at 字段")
    
    def test_all_extended_fields_present(self):
        """验证所有扩展字段都存在"""
        required_fields = ['abandoned_by', 'abandoned_at', 'expiry_checked_at']
        
        for field in required_fields:
            assert hasattr(BettingPlan, field), f"BettingPlan 模型应该有 {field} 属性"
        
        print("✓ 所有扩展字段都已添加到 BettingPlan 模型")
