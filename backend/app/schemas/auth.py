"""
认证相关的 Pydantic 模式
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=2, max_length=50)
    gender: str
    age: int = Field(..., ge=13, le=120)
    height: float = Field(..., ge=100.0, le=250.0)
    current_weight: float = Field(..., ge=30.0, le=300.0)


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResult(BaseModel):
    """认证结果"""
    user_id: str
    email: str
    nickname: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    """Google 登录请求"""
    id_token: str
