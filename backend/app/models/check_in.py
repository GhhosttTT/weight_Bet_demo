"""
打卡记录数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text, Date, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ReviewStatus(str, enum.Enum):
    """审核状态枚举"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝


class CheckIn(Base):
    """打卡记录模型"""
    __tablename__ = "check_ins"
    
    # 主键
    id = Column(String(36), primary_key=True, index=True)
    
    # 关联
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("betting_plans.id"), nullable=False, index=True)
    
    # 打卡数据
    weight = Column(Float, nullable=False)
    check_in_date = Column(Date, nullable=False, index=True)
    photo_url = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    
    # 审核信息
    review_status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.APPROVED, nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 唯一约束: 每个用户每天只能打卡一次
    __table_args__ = (
        UniqueConstraint('user_id', 'plan_id', 'check_in_date', name='uq_user_plan_date'),
    )
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    plan = relationship("BettingPlan")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, weight={self.weight}, date={self.check_in_date})>"
