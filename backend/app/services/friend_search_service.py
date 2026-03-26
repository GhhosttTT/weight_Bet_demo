"""
好友搜索服务
"""
import re
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserSearchResult
from app.logger import get_logger

logger = get_logger()


class FriendSearchService:
    """好友搜索服务类"""
    
    # 邮箱格式验证正则表达式
    # 不允许连续的点、开头或结尾的点
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$|^[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
    )
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 邮箱格式是否有效
        """
        if not email or not isinstance(email, str):
            return False
        
        # 检查是否包含连续的点
        if '..' in email:
            return False
        
        return bool(FriendSearchService.EMAIL_REGEX.match(email))
    
    @staticmethod
    def search_by_email(
        db: Session,
        email: str
    ) -> Optional[UserSearchResult]:
        """
        通过邮箱搜索用户
        
        Args:
            db: 数据库会话
            email: 邮箱地址
            
        Returns:
            Optional[UserSearchResult]: 用户搜索结果，如果未找到则返回 None
            
        Raises:
            HTTPException: 邮箱格式无效
        """
        # 验证邮箱格式
        if not FriendSearchService.validate_email_format(email):
            logger.warning("Invalid email format: {}", email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式无效"
            )
        
        # 查询用户
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.info("User not found for email: {}", email)
            return None
        
        # 构建搜索结果（只返回公开信息）
        result = UserSearchResult(
            user_id=user.id,
            nickname=user.nickname,
            age=user.age,
            gender=user.gender
        )
        
        logger.info("User found for email {}: {}", email, user.id)
        
        return result
