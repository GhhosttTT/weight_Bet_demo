"""测试登录功能"""
from app.database import SessionLocal
from app.models.user import User
from app.models.balance import Balance
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建数据库会话
db = SessionLocal()

try:
    # 检查用户是否存在
    user = db.query(User).filter(User.email == "1612@qq.com").first()
    
    if user:
        print(f"✓ 用户已存在: {user.email}")
        print(f"  - ID: {user.id}")
        print(f"  - 昵称: {user.nickname}")
    else:
        print("✗ 用户不存在，正在创建测试用户...")
        
        # 创建测试用户
        hashed_password = pwd_context.hash("123456")
        new_user = User(
            email="1612@qq.com",
            password_hash=hashed_password,
            nickname="测试用户",
            age=25,
            gender="male",
            height=175.0,
            current_weight=80.0
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 创建余额记录
        balance = Balance(
            user_id=new_user.id,
            available_balance=1000.0,
            frozen_balance=0.0
        )
        db.add(balance)
        db.commit()
        
        print(f"✓ 测试用户创建成功: {new_user.email}")
        print(f"  - ID: {new_user.id}")
        print(f"  - 密码: 123456")
        print(f"  - 初始余额: 1000.0")
        
finally:
    db.close()

print("\n现在可以使用以下凭据登录:")
print("  邮箱: 1612@qq.com")
print("  密码: 123456")
