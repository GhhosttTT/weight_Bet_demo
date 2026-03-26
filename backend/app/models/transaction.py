"""
交易记录数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class TransactionType(str, enum.Enum):
    """交易类型枚举"""
    FREEZE = "freeze"
    UNFREEZE = "unfreeze"
    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    REFUND = "refund"
    CHARGE = "charge"


class TransactionStatus(str, enum.Enum):
    """交易状态枚举"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Transaction(Base):
    """交易记录模型"""
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    related_plan_id = Column(String(36), ForeignKey("betting_plans.id"), nullable=True)
    related_settlement_id = Column(String(36), ForeignKey("settlements.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount})>"
