"""
为现有用户创建余额记录
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User
from app.models.balance import Balance

def fix_balances():
    db = SessionLocal()
    try:
        # 获取所有用户
        users = db.query(User).all()
        print(f"找到 {len(users)} 个用户")
        
        created_count = 0
        for user in users:
            # 检查是否已有余额记录
            existing_balance = db.query(Balance).filter(Balance.user_id == user.id).first()
            if not existing_balance:
                # 创建余额记录
                new_balance = Balance(
                    user_id=user.id,
                    available_balance=0.0,
                    frozen_balance=0.0
                )
                db.add(new_balance)
                created_count += 1
                print(f"✅ 为用户 {user.nickname} ({user.email}) 创建余额记录")
        
        db.commit()
        print(f"\n完成! 共创建 {created_count} 条余额记录")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_balances()
