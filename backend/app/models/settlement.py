"""
结算记录数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Settlement(Base):
    """结算记录模型"""
    __tablename__ = "settlements"
    
    id = Column(String(36), primary_key=True, index=True)
    plan_id = Column(String(36), ForeignKey("betting_plans.id"), unique=True, nullable=False, index=True)
    
    # 结算结果
    creator_achieved = Column(Boolean, nullable=False)
    participant_achieved = Column(Boolean, nullable=False)
    creator_final_weight = Column(Float, nullable=False)
    participant_final_weight = Column(Float, nullable=False)
    creator_weight_loss = Column(Float, nullable=False)
    participant_weight_loss = Column(Float, nullable=False)
    
    # 金额分配
    creator_amount = Column(Float, nullable=False)
    participant_amount = Column(Float, nullable=False)
    platform_fee = Column(Float, nullable=False)
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 仲裁标记
    in_arbitration = Column(Boolean, server_default="false", nullable=False)
    arbitration_fee = Column(Float, nullable=True)  # 仲裁费用（15%）
    
    # 时间戳
    settlement_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    plan = relationship("BettingPlan")
    
    def __repr__(self):
        return f"<Settlement(id={self.id}, plan_id={self.plan_id})>"
