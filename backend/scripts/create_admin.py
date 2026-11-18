"""将已有用户提升为后台管理员。

用法：python scripts/create_admin.py user@example.com
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.user import User


if len(sys.argv) != 2:
    raise SystemExit("用法: python scripts/create_admin.py <email>")

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == sys.argv[1].strip().lower()).first()
    if not user:
        raise SystemExit("找不到该用户，请先注册普通账号")
    user.role = "admin"
    db.commit()
    print(f"管理员已启用: {user.email} ({user.id})")
finally:
    db.close()
