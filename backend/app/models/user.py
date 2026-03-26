"""
用户数据模型
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class Gender(str, enum.Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    # 主键
    id = Column(String(36), primary_key=True, index=True)
    
    # 认证信息
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # 个人信息
    nickname = Column(String(50), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    age = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)  # 单位: cm
    current_weight = Column(Float, nullable=False)  # 单位: kg
    target_weight = Column(Float, nullable=True)  # 单位: kg
    
    # 支付信息
    payment_method_id = Column(String(255), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, nickname={self.nickname})>"
