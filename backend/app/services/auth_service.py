"""
认证服务
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import User, Gender
from app.models.balance import Balance
from app.models.refresh_token import RefreshToken
from app.models.device_token import DeviceToken
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResult
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.logger import get_logger
from app.config import settings

logger = get_logger()


class AuthService:
    """认证服务类"""

    @staticmethod
    def _issue_token_pair(db: Session, user: User):
        """创建访问令牌和可撤销的 Refresh Token 会话。"""
        token_id = str(uuid.uuid4())
        refresh_token = create_refresh_token({"sub": user.id, "jti": token_id})
        record = RefreshToken(
            id=token_id,
            user_id=user.id,
            token_hash=hashlib.sha256(refresh_token.encode("utf-8")).hexdigest(),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(record)
        access_token = create_access_token({"sub": user.id, "jti": token_id})
        return access_token, refresh_token, record
    
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
        access_token, refresh_token, _ = AuthService._issue_token_pair(db, new_user)
        db.commit()
        
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
        access_token, refresh_token, _ = AuthService._issue_token_pair(db, user)
        db.commit()
        
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
        
        token_id = payload.get("jti")
        if not token_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请重新登录")

        token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        stored_token = db.query(RefreshToken).filter(
            RefreshToken.id == token_id,
            RefreshToken.user_id == user_id,
        ).with_for_update().first()
        if (
            not stored_token
            or not secrets.compare_digest(stored_token.token_hash, token_hash)
            or not stored_token.is_active()
        ):
            logger.warning("Token refresh failed: revoked or unknown token for user {}", user_id)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌已失效")

        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("Token refresh failed: user {} not found", user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        logger.info("Token refreshed successfully for user: {}", user_id)
        
        # 轮换令牌：旧令牌立即吊销，重放旧令牌会失败。
        new_access_token, new_refresh_token, replacement = AuthService._issue_token_pair(db, user)
        stored_token.revoked_at = datetime.utcnow()
        stored_token.replaced_by_id = replacement.id
        db.commit()
        
        return AuthResult(
            user_id=user.id,
            email=user.email,
            nickname=user.nickname,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    
    @staticmethod
    def google_login(db: Session, id_token_str: str, nonce: str = None) -> AuthResult:
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
            client_ids = settings.google_client_ids_list
            if not client_ids:
                logger.error("Google login is not configured: GOOGLE_CLIENT_IDS is empty")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Google 登录尚未配置"
                )

            # 必须限制 audience，避免把发给其他 Google 应用的 ID Token
            # 当成本应用的登录凭证。
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                client_ids[0] if len(client_ids) == 1 else client_ids
            )

            if idinfo.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
                raise ValueError("invalid issuer")
            if idinfo.get("email_verified") is not True:
                raise ValueError("email is not verified")
            if nonce is not None and idinfo.get("nonce") != nonce:
                raise ValueError("invalid nonce")
            
            # 获取用户信息
            email = (idinfo.get("email") or "").strip().lower()
            subject = (idinfo.get("sub") or "").strip()
            
            if not email or not subject:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google 身份信息不完整"
                )

            name = idinfo.get("name") or email.split("@")[0]
            
            # 查找或创建用户
            user = db.query(User).filter(User.google_subject == subject).first()
            email_user = db.query(User).filter(User.email == email).first()

            if user and email_user and user.id != email_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Google 身份与邮箱账号绑定冲突"
                )
            if user is None:
                user = email_user
            
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
                    target_weight=None,
                    google_subject=subject,
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
                if user.google_subject and user.google_subject != subject:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="该账号已绑定其他 Google 身份"
                    )
                if user.google_subject is None:
                    user.google_subject = subject
                    db.commit()
                    db.refresh(user)
                logger.info("Existing user logged in via Google: {}", user.id)
            
            # 生成令牌
            access_token, refresh_token, _ = AuthService._issue_token_pair(db, user)
            db.commit()
            
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

    @staticmethod
    def revoke_refresh_token(db: Session, refresh_token: str) -> None:
        """吊销一个 Refresh Token；最后一个会话退出时清理该用户推送 Token。"""
        payload = decode_token(refresh_token)
        token_id = payload.get("jti") if payload else None
        if not token_id:
            return
        record = db.query(RefreshToken).filter(RefreshToken.id == token_id).first()
        if record and record.revoked_at is None:
            user_id = record.user_id
            record.revoked_at = datetime.utcnow()
            db.commit()
            active_sessions = db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.utcnow(),
            ).count()
            if active_sessions == 0:
                db.query(DeviceToken).filter(DeviceToken.user_id == user_id).delete(
                    synchronize_session=False
                )
                db.commit()
