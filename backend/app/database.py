"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Normalize sqlite relative paths to absolute paths to avoid cwd-dependent DB files
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:"):
    # Extract path part
    path = database_url.replace("sqlite:///", "").replace("sqlite://", "")
    if not os.path.isabs(path):
        # make absolute relative to the backend package root
        base_dir = os.path.dirname(os.path.dirname(__file__))  # app/ -> backend/app -> backend
        abs_path = os.path.abspath(os.path.join(base_dir, path))
    else:
        abs_path = path
    # ensure directory exists
    db_dir = os.path.dirname(abs_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    # set normalized URL
    database_url = f"sqlite:///{abs_path}"

# 创建数据库引擎
# SQLite 需要特殊配置
if "sqlite" in database_url:
    engine = create_engine(
        database_url,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}  # SQLite 特殊配置
    )
else:
    engine = create_engine(
        database_url,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
