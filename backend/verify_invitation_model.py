"""
验证 Invitation 模型的完整性
"""
from app.models.invitation import Invitation, InvitationStatus
from app.models.betting_plan import BettingPlan
from app.models.user import User
from sqlalchemy import inspect


def verify_invitation_model():
    """验证 Invitation 模型是否符合设计要求"""
    
    print("=== 验证 Invitation 模型 ===\n")
    
    # 1. 验证 InvitationStatus 枚举
    print("1. InvitationStatus 枚举值:")
    expected_statuses = {"PENDING", "VIEWED", "ACCEPTED", "REJECTED", "EXPIRED"}
    actual_statuses = {status.name for status in InvitationStatus}
    
    if expected_statuses == actual_statuses:
        print(f"   ✓ 所有状态值正确: {', '.join(sorted(actual_statuses))}")
    else:
        print(f"   ✗ 状态值不匹配!")
        print(f"     期望: {expected_statuses}")
        print(f"     实际: {actual_statuses}")
        return False
    
    # 2. 验证 Invitation 类的字段
    print("\n2. Invitation 类字段:")
    mapper = inspect(Invitation)
    columns = {col.key: str(col.type) for col in mapper.columns}
    
    required_fields = {
        "id": "VARCHAR(36)",
        "plan_id": "VARCHAR(36)",
        "inviter_id": "VARCHAR(36)",
        "invitee_email": "VARCHAR(255)",
        "invitee_id": "VARCHAR(36)",
        "status": "ENUM",
        "sent_at": "DATETIME",
        "viewed_at": "DATETIME",
        "responded_at": "DATETIME",
    }
    
    for field, expected_type in required_fields.items():
        if field in columns:
            actual_type = columns[field]
            print(f"   ✓ {field}: {actual_type}")
        else:
            print(f"   ✗ 缺少字段: {field}")
            return False
    
    # 3. 验证关系映射
    print("\n3. 关系映射:")
    relationships = {rel.key: rel.mapper.class_.__name__ for rel in mapper.relationships}
    
    expected_relationships = {
        "plan": "BettingPlan",
        "inviter": "User",
        "invitee": "User",
    }
    
    for rel_name, expected_class in expected_relationships.items():
        if rel_name in relationships:
            actual_class = relationships[rel_name]
            if actual_class == expected_class:
                print(f"   ✓ {rel_name} -> {actual_class}")
            else:
                print(f"   ✗ {rel_name} 关系类型错误: 期望 {expected_class}, 实际 {actual_class}")
                return False
        else:
            print(f"   ✗ 缺少关系: {rel_name}")
            return False
    
    # 4. 验证约束
    print("\n4. 表约束:")
    table = Invitation.__table__
    
    # 检查唯一约束
    unique_columns = []
    for constraint in table.constraints:
        if hasattr(constraint, 'columns'):
            for col in constraint.columns:
                if col.unique:
                    unique_columns.append(col.name)
    
    # 检查 plan_id 的唯一性
    plan_id_col = table.c.plan_id
    if plan_id_col.unique:
        print(f"   ✓ plan_id 具有唯一约束")
    else:
        print(f"   ✗ plan_id 缺少唯一约束")
        return False
    
    # 5. 验证索引
    print("\n5. 索引:")
    indexed_columns = [col.name for col in table.columns if col.index]
    expected_indexes = ["id", "plan_id", "inviter_id", "invitee_email", "invitee_id", "status"]
    
    for idx_col in expected_indexes:
        if idx_col in indexed_columns:
            print(f"   ✓ {idx_col} 已建立索引")
        else:
            print(f"   ⚠ {idx_col} 未建立索引 (可能影响查询性能)")
    
    print("\n=== 验证完成 ===")
    print("✓ Invitation 模型定义正确，符合设计要求")
    return True


if __name__ == "__main__":
    try:
        verify_invitation_model()
    except Exception as e:
        print(f"\n✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
