"""
对赌计划数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class PlanStatus(str, enum.Enum):
    """计划状态枚举"""
    PENDING = "pending"  # 等待对方接受
    WAITING_DOUBLE_CHECK = "waiting_double_check"  # 待二次确认（被邀请人已接受，等待创建者确认）
    ACTIVE = "active"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期


class BettingPlan(Base):
    """对赌计划模型"""
    __tablename__ = "betting_plans"
    
    # 主键
    id = Column(String(36), primary_key=True, index=True)
    
    # 参与者
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # 计划状态
    status = Column(SQLEnum(PlanStatus), default=PlanStatus.PENDING, nullable=False, index=True)
    
    # 赌金
    bet_amount = Column(Float, nullable=False)
    
    # 时间
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # 描述
    description = Column(Text, nullable=True)
    
    # 创建者目标
    creator_initial_weight = Column(Float, nullable=False)
    creator_target_weight = Column(Float, nullable=False)
    creator_target_weight_loss = Column(Float, nullable=False)
    
    # 参与者目标
    participant_initial_weight = Column(Float, nullable=True)
    participant_target_weight = Column(Float, nullable=True)
    participant_target_weight_loss = Column(Float, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 放弃计划相关字段
    abandoned_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    abandoned_at = Column(DateTime(timezone=True), nullable=True)
    expiry_checked_at = Column(DateTime(timezone=True), nullable=True)

    # pending double-check 标记（当参与者接受并需要创建者确认时设置）
    pending_double_check = Column(Boolean, server_default="false", nullable=False)

    # 关系
    creator = relationship("User", foreign_keys=[creator_id])
    participant = relationship("User", foreign_keys=[participant_id])
    invitation = relationship("Invitation", back_populates="plan", uselist=False)
    
    def __repr__(self):
        return f"<BettingPlan(id={self.id}, status={self.status}, bet_amount={self.bet_amount})>"
