"""
认证 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResult, RefreshTokenRequest, GoogleLoginRequest
from app.services.auth_service import AuthService
from app.logger import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/register", response_model=AuthResult, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    - **email**: 邮箱地址
    - **password**: 密码 (至少 8 个字符)
    - **nickname**: 昵称 (2-50 个字符)
    - **gender**: 性别 (male/female/other)
    - **age**: 年龄 (13-120)
    - **height**: 身高 (100-250 cm)
    - **current_weight**: 当前体重 (30-300 kg)
    """
    return AuthService.register(db, request)


@router.post("/login", response_model=AuthResult)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    """
    return AuthService.login(db, request)


@router.post("/refresh", response_model=AuthResult)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    return AuthService.refresh_token(db, request.refresh_token)


@router.post("/logout")
def logout(
    request: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db),
):
    """
    用户登出
    
    客户端删除本地令牌；如果提交 Refresh Token，服务端同步吊销该会话。
    """
    if request and request.refresh_token:
        AuthService.revoke_refresh_token(db, request.refresh_token)
    return {"message": "登出成功"}


@router.post("/google", response_model=AuthResult)
def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Google 第三方登录
    
    - **id_token**: Google ID Token
    """
    return AuthService.google_login(db, request.id_token)
