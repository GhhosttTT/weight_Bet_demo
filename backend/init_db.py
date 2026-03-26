"""初始化数据库（更健壮和可见的输出）"""
import os
import sqlite3
from sqlalchemy import create_engine
from app.config import settings
from app.database import engine, Base

# 导入模型，确保 SQLAlchemy metadata 包含它们
from app.models.user import User
from app.models.balance import Balance
from app.models.transaction import Transaction
from app.models.betting_plan import BettingPlan
from app.models.check_in import CheckIn
from app.models.settlement import Settlement
from app.models.invitation import Invitation
from app.models.device_token import DeviceToken

print(f"PWD={os.getcwd()}")
print(f"Using DATABASE_URL={settings.DATABASE_URL}")

# 如果使用 sqlite 文件，确保目录存在并创建文件
if settings.DATABASE_URL.startswith("sqlite:"):
    path = settings.DATABASE_URL.replace("sqlite:///,", "")
    path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory for sqlite DB: {db_dir}")
    if not os.path.exists(path):
        open(path, 'a').close()
        print(f"Created sqlite db file at: {path}")
    else:
        print(f"Sqlite db file already exists: {path}")

# 在默认 engine 上创建所有表
try:
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表在 settings 指定的引擎上创建/确认成功")
except Exception as e:
    print("在 settings 引擎上创建表时出错:", e)

# 同时创建 tests 可能直接打开的嵌套文件 backend/weight_loss_betting.db
if settings.DATABASE_URL.startswith("sqlite:"):
    db_path = settings.DATABASE_URL.replace("sqlite:///,", "")
    db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    basename = os.path.basename(db_path)
    nested_path = os.path.abspath(os.path.join(os.getcwd(), 'backend', basename))
    try:
        nested_dir = os.path.dirname(nested_path)
        if nested_dir and not os.path.exists(nested_dir):
            os.makedirs(nested_dir, exist_ok=True)
        # touch file
        if not os.path.exists(nested_path):
            open(nested_path, 'a').close()
            print(f"Created nested sqlite db file at: {nested_path}")
        else:
            print(f"Nested sqlite db file already exists: {nested_path}")
        # create engine and tables
        alt_engine = create_engine(f"sqlite:///{nested_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=alt_engine)
        print(f"✓ 数据库表在嵌套文件 {nested_path} 上创建/确认成功")
    except Exception as e:
        print("在嵌套 sqlite 文件上创建表时出错:", e)

# 列出 sqlite 表（若适用）
if settings.DATABASE_URL.startswith("sqlite:"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n数据库中的表 (settings DB):")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print("无法列出 settings sqlite 表:", e)

    # list nested
    try:
        conn = sqlite3.connect(nested_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n数据库中的表 (nested DB):")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print("无法列出嵌套 sqlite 表:", e)
