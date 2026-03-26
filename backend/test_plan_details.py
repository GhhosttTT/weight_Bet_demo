"""测试计划详情查询"""
from app.database import SessionLocal
from app.models.betting_plan import BettingPlan
from sqlalchemy.orm import joinedload

db = SessionLocal()

try:
    # 测试查询 - 使用 joinedload 预加载关联对象
    plan = db.query(BettingPlan).options(
        joinedload(BettingPlan.creator),
        joinedload(BettingPlan.participant)
    ).filter(BettingPlan.id == 'dd06d082-143b-4d61-b9dc-4d8859583757').first()
    
    if plan:
        print(f"✓ Plan ID: {plan.id}")
        print(f"✓ Creator: {plan.creator}")
        print(f"✓ Creator nickname: {plan.creator.nickname if plan.creator else None}")
        print(f"✓ Creator email: {plan.creator.email if plan.creator else None}")
    else:
        print("✗ Plan not found")
finally:
    db.close()
