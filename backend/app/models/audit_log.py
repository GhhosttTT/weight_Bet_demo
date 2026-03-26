"""
审计日志数据模型
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"
    
    # 主键
    id = Column(String(36), primary_key=True, index=True)
    
    # 用户信息
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # 操作信息
    action = Column(String(100), nullable=False, index=True)  # 操作类型
    resource_type = Column(String(50), nullable=False)  # 资源类型
    resource_id = Column(String(36), nullable=True)  # 资源ID
    
    # 详细信息
    details = Column(JSON, nullable=True)  # 操作详情
    ip_address = Column(String(45), nullable=True)  # IP地址
    user_agent = Column(Text, nullable=True)  # 用户代理
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # 关系
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
