"""
数据库表检查脚本
验证所有需要的表是否已创建
"""
import sys
from pathlib import Path
from sqlalchemy import inspect

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine

def check_database_tables():
    """检查数据库中的所有表"""
    print("=" * 60)
    print("数据库表检查报告")
    print("=" * 60)
    
    # 获取数据库检查器
    inspector = inspect(engine)
    
    # 获取所有表名
    tables = inspector.get_table_names()
    
    print(f"\n✅ 数据库连接成功")
    print(f"📊 共找到 {len(tables)} 个表\n")
    
    # 定义需要的表及其说明
    required_tables = {
        'users': '用户表',
        'balances': '余额表',
        'betting_plans': '对赌计划表',
        'check_ins': '打卡记录表',
        'settlements': '结算记录表',
        'transactions': '交易记录表',
        'audit_logs': '审计日志表',
        'user_badges': '用户徽章表',
        'comments': '评论表',
        'device_tokens': '设备令牌表',
        'disputes': '争议记录表'
    }
    
    print("=" * 60)
    print("必需表检查")
    print("=" * 60)
    
    missing_tables = []
    existing_tables = []
    
    for table_name, description in required_tables.items():
        if table_name in tables:
            print(f"✅ {table_name:20s} - {description}")
            existing_tables.append(table_name)
        else:
            print(f"❌ {table_name:20s} - {description} (缺失)")
            missing_tables.append(table_name)
    
    print("\n" + "=" * 60)
    print("表结构详情")
    print("=" * 60)
    
    for table_name in sorted(existing_tables):
        print(f"\n📋 表: {table_name}")
        print("-" * 60)
        
        # 获取列信息
        columns = inspector.get_columns(table_name)
        print(f"  列数: {len(columns)}")
        print("  列名:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            col_type = str(col['type'])
            print(f"    - {col['name']:25s} {col_type:20s} {nullable}")
        
        # 获取主键
        pk = inspector.get_pk_constraint(table_name)
        if pk and pk['constrained_columns']:
            print(f"  主键: {', '.join(pk['constrained_columns'])}")
        
        # 获取外键
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print("  外键:")
            for fk in fks:
                print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)
    
    print(f"\n✅ 已创建的表: {len(existing_tables)}/{len(required_tables)}")
    
    if missing_tables:
        print(f"❌ 缺失的表: {len(missing_tables)}")
        for table in missing_tables:
            print(f"   - {table}")
        print("\n⚠️  警告: 数据库表不完整，某些功能可能无法正常工作")
        return False
    else:
        print("✅ 所有必需的表都已创建")
        
        # 检查额外的表
        extra_tables = set(tables) - set(required_tables.keys())
        if extra_tables:
            print(f"\n📝 发现额外的表: {len(extra_tables)}")
            for table in sorted(extra_tables):
                print(f"   - {table}")
        
        print("\n🎉 数据库结构完整，可以正常使用！")
        return True

def test_database_operations():
    """测试基本的数据库操作"""
    print("\n" + "=" * 60)
    print("数据库操作测试")
    print("=" * 60)
    
    from app.database import SessionLocal
    from app.models.user import User
    
    db = SessionLocal()
    
    try:
        # 测试查询
        print("\n🔍 测试查询操作...")
        user_count = db.query(User).count()
        print(f"✅ 用户表查询成功，当前用户数: {user_count}")
        
        # 如果有用户，显示第一个用户的信息
        if user_count > 0:
            first_user = db.query(User).first()
            print(f"   示例用户: {first_user.email} ({first_user.nickname})")
        
        return True
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("\n")
    
    # 检查表结构
    tables_ok = check_database_tables()
    
    # 测试数据库操作
    if tables_ok:
        operations_ok = test_database_operations()
        
        if operations_ok:
            print("\n" + "=" * 60)
            print("✅ 数据库检查完成，一切正常！")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("⚠️  数据库表存在但操作测试失败")
            print("=" * 60)
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ 数据库表不完整")
        print("=" * 60)
        print("\n建议运行: python init_db.py")
        sys.exit(1)
