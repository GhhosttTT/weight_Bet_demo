"""平台收入账本。"""
from sqlalchemy import Column, DateTime, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PlatformLedgerEntry(Base):
    """记录从用户资金池中扣除、归属于平台的结算收入。"""

    __tablename__ = "platform_ledger_entries"

    id = Column(String(36), primary_key=True, index=True)
    settlement_id = Column(
        String(36), ForeignKey("settlements.id"), unique=True, nullable=False, index=True
    )
    amount = Column(Numeric(12, 2, asdecimal=False), nullable=False)
    entry_type = Column(String(40), nullable=False, default="settlement_fee")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    settlement = relationship("Settlement")
