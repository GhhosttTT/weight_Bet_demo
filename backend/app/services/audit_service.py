"""
审计日志服务
"""
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.audit_log import AuditLog
from app.logger import get_logger

logger = get_logger()


class AuditService:
    """审计日志服务类"""
    
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        记录审计日志
        
        Args:
            db: 数据库会话
            action: 操作类型 (如: user.login, user.delete, plan.create)
            resource_type: 资源类型 (如: user, betting_plan, transaction)
            user_id: 用户ID (可选)
            resource_id: 资源ID (可选)
            details: 操作详情 (可选)
            ip_address: IP地址 (可选)
            user_agent: 用户代理 (可选)
            
        Returns:
            AuditLog: 审计日志记录
        """
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        logger.info("Audit log created: action={}, user_id={}, resource_type={}", action, user_id, resource_type)
        
        return audit_log
    
    @staticmethod
    def log_from_request(
        db: Session,
        request: Request,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        从请求中提取信息并记录审计日志
        
        Args:
            db: 数据库会话
            request: FastAPI请求对象
            action: 操作类型
            resource_type: 资源类型
            user_id: 用户ID (可选)
            resource_id: 资源ID (可选)
            details: 操作详情 (可选)
            
        Returns:
            AuditLog: 审计日志记录
        """
        # 提取IP地址
        ip_address = request.client.host if request.client else None
        
        # 提取User-Agent
        user_agent = request.headers.get("user-agent")
        
        return AuditService.log_action(
            db=db,
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def query_logs(
        db: Session,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        查询审计日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID (可选)
            action: 操作类型 (可选)
            resource_type: 资源类型 (可选)
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[AuditLog]: 审计日志列表
        """
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        query = query.order_by(AuditLog.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
