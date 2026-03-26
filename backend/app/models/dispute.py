"""
争议记录数据模型
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class DisputeStatus(str, enum.Enum):
    """争议状态"""
    PENDING = "pending"  # 待处理
    UNDER_REVIEW = "under_review"  # 审核中
    RESOLVED = "resolved"  # 已解决
    REJECTED = "rejected"  # 已拒绝


class Dispute(Base):
    """争议记录模型"""
    __tablename__ = "disputes"
    
    id = Column(String(36), primary_key=True, index=True)
    settlement_id = Column(String(36), ForeignKey("settlements.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # 争议内容
    reason = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # 争议状态
    status = Column(SQLEnum(DisputeStatus), default=DisputeStatus.PENDING, nullable=False)
    
    # 管理员处理
    admin_notes = Column(Text, nullable=True)
    resolved_by = Column(String(36), nullable=True)  # 处理管理员 ID
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    settlement = relationship("Settlement")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Dispute(id={self.id}, settlement_id={self.settlement_id}, status={self.status})>"
