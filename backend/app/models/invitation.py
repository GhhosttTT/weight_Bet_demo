"""
邀请数据模型
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class InvitationStatus(str, enum.Enum):
    """邀请状态枚举"""
    PENDING = "pending"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Invitation(Base):
    """邀请模型"""
    __tablename__ = "invitations"
    
    # 主键
    id = Column(String(36), primary_key=True, index=True)
    
    # 关联计划和用户
    plan_id = Column(String(36), ForeignKey("betting_plans.id"), nullable=False, unique=True, index=True)
    inviter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    invitee_email = Column(String(255), nullable=False, index=True)
    invitee_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # 状态
    status = Column(
        SQLEnum(InvitationStatus, values_callable=lambda x: [e.value for e in x]), 
        default=InvitationStatus.PENDING, 
        nullable=False,
        index=True
    )
    
    # 时间戳
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    plan = relationship("BettingPlan", back_populates="invitation")
    inviter = relationship("User", foreign_keys=[inviter_id])
    invitee = relationship("User", foreign_keys=[invitee_id])
    
    # 约束
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'viewed', 'accepted', 'rejected', 'expired')",
            name="check_invitation_status"
        ),
    )
    
    def __repr__(self):
        return f"<Invitation(id={self.id}, plan_id={self.plan_id}, status={self.status})>"
