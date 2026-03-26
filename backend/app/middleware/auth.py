"""
认证中间件
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token
from app.logger import get_logger

logger = get_logger()

# HTTP Bearer 认证方案
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    
    Args:
        credentials: HTTP 认证凭证
        db: 数据库会话
        
    Returns:
        User: 当前用户
        
    Raises:
        HTTPException: 令牌无效或用户不存在
    """
    token = credentials.credentials
    
    # 解码令牌
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        logger.warning("Authentication failed: invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("Authentication failed: user {} not found", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    """获取当前用户 ID"""
    return current_user.id
