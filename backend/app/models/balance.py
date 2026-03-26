"""
账户余额数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Balance(Base):
    """账户余额模型"""
    __tablename__ = "balances"
    
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True, index=True)
    available_balance = Column(Float, default=0.0, nullable=False)
    frozen_balance = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 约束: 余额不能为负
    __table_args__ = (
        CheckConstraint('available_balance >= 0', name='check_available_balance_positive'),
        CheckConstraint('frozen_balance >= 0', name='check_frozen_balance_positive'),
    )
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<Balance(user_id={self.user_id}, available={self.available_balance}, frozen={self.frozen_balance})>"
