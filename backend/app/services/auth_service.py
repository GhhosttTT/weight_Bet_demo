"""
认证服务
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import User, Gender
from app.models.balance import Balance
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResult
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.logger import get_logger
from app.config import settings

logger = get_logger()


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def register(db: Session, request: RegisterRequest) -> AuthResult:
        """
        用户注册
        
        Args:
            db: 数据库会话
            request: 注册请求
            
        Returns:
            AuthResult: 认证结果
            
        Raises:
            HTTPException: 邮箱已被注册
        """
        # 检查邮箱是否已注册
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            logger.warning("Registration failed: email {} already exists", request.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建新用户
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(request.password)
        
        new_user = User(
            id=user_id,
            email=request.email,
            password_hash=hashed_password,
            nickname=request.nickname,
            gender=Gender(request.gender),
            age=request.age,
            height=request.height,
            current_weight=request.current_weight,
            target_weight=None
        )
        
        db.add(new_user)
        
        # 初始化用户余额账户
        new_balance = Balance(
            user_id=user_id,
            available_balance=0.0,
            frozen_balance=0.0
        )
        db.add(new_balance)
        
        db.commit()
        db.refresh(new_user)
        
        logger.info("User registered successfully: {}", user_id)
        
        # 生成令牌
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})
        
        return AuthResult(
            user_id=user_id,
            email=new_user.email,
            nickname=new_user.nickname,
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def login(db: Session, request: LoginRequest) -> AuthResult:
        """
        用户登录
        
        Args:
            db: 数据库会话
            request: 登录请求
            
        Returns:
            AuthResult: 认证结果
            
        Raises:
            HTTPException: 用户不存在或密码错误
        """
        # 查找用户
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.warning("Login failed: user {} not found", request.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 验证密码
        if not verify_password(request.password, user.password_hash):
            logger.warning("Login failed: invalid password for user {}", request.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        logger.info("User logged in successfully: {}", user.id)
        
        # 生成令牌
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return AuthResult(
            user_id=user.id,
            email=user.email,
            nickname=user.nickname,
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> AuthResult:
        """
        刷新访问令牌
        
        Args:
            db: 数据库会话
            refresh_token: 刷新令牌
            
        Returns:
            AuthResult: 认证结果
            
        Raises:
            HTTPException: 令牌无效或过期
        """
        from app.utils.security import decode_token
        
        # 解码令牌
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("Token refresh failed: invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("Token refresh failed: user {} not found", user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        logger.info("Token refreshed successfully for user: {}", user_id)
        
        # 生成新令牌
        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})
        
        return AuthResult(
            user_id=user.id,
            email=user.email,
            nickname=user.nickname,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    
    @staticmethod
    def google_login(db: Session, id_token_str: str) -> AuthResult:
        """
        Google 第三方登录
        
        Args:
            db: 数据库会话
            id_token_str: Google ID Token
            
        Returns:
            AuthResult: 认证结果
            
        Raises:
            HTTPException: Token 验证失败
        """
        try:
            # 验证 Google ID Token
            # 注意: 生产环境需要配置正确的 CLIENT_ID
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(),
                None  # 在生产环境应该传入 Google Client ID
            )
            
            # 获取用户信息
            email = idinfo.get('email')
            name = idinfo.get('name', email.split('@')[0])
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无法从 Google 获取邮箱信息"
                )
            
            # 查找或创建用户
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # 创建新用户
                user_id = str(uuid.uuid4())
                user = User(
                    id=user_id,
                    email=email,
                    password_hash=hash_password(str(uuid.uuid4())),  # 随机密码
                    nickname=name,
                    gender=Gender.OTHER,  # 默认性别
                    age=25,  # 默认年龄
                    height=170.0,  # 默认身高
                    current_weight=70.0,  # 默认体重
                    target_weight=None
                )
                db.add(user)
                
                # 初始化余额
                new_balance = Balance(
                    user_id=user_id,
                    available_balance=0.0,
                    frozen_balance=0.0
                )
                db.add(new_balance)
                
                db.commit()
                db.refresh(user)
                
                logger.info("New user created via Google login: {}", user_id)
            else:
                logger.info("Existing user logged in via Google: {}", user.id)
            
            # 生成令牌
            access_token = create_access_token({"sub": user.id})
            refresh_token = create_refresh_token({"sub": user.id})
            
            return AuthResult(
                user_id=user.id,
                email=user.email,
                nickname=user.nickname,
                access_token=access_token,
                refresh_token=refresh_token
            )
            
        except ValueError as e:
            logger.error("Google login failed: {}", str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 Google ID Token"
            )
