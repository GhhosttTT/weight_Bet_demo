"""
结算选择数据模型
记录用户在结算时对自己和对方是否达成目标的选择
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SettlementChoice(Base):
    """用户结算选择模型"""
    __tablename__ = "settlement_choices"
    
    id = Column(String(36), primary_key=True, index=True)
    plan_id = Column(String(36), ForeignKey("betting_plans.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # 用户选择
    self_achieved = Column(Boolean, nullable=False)  # 自己是否达成
    opponent_achieved = Column(Boolean, nullable=False)  # 对方是否达成
    
    # 选择轮次（1=第一次，2=第二次，3=第三次）
    round = Column(Integer, nullable=False, default=1)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    plan = relationship("BettingPlan")
    user = relationship("User")
    
    def __repr__(self):
        return f"<SettlementChoice(id={self.id}, plan_id={self.plan_id}, user_id={self.user_id}, round={self.round})>"
