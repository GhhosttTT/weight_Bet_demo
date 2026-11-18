"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_ECHO: bool = False
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    SECRET_KEY: str = "test-secret-key-for-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Stripe 配置
    STRIPE_SECRET_KEY: str = "sk_test_dummy"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_dummy"
    STRIPE_WEBHOOK_SECRET: str = "whsec_test_dummy"
    PAYMENT_PROVIDER: str = "demo"
    STRIPE_CURRENCY: str = "cny"
    
    # Firebase 配置
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"

    # Google Identity Services。多个客户端 ID 用逗号分隔，生产环境必须配置。
    GOOGLE_CLIENT_IDS: str = ""
    
    # 推荐模型配置
    RECOMMENDATION_MODEL_URL: str = "http://localhost:8001"
    
    # 应用配置
    APP_NAME: str = "减肥对赌 APP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    SCHEDULER_API_KEY: Optional[str] = None
    
    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """获取允许的跨域来源列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def google_client_ids_list(self) -> List[str]:
        """返回启用的 Google OAuth Client ID 列表。"""
        return [item.strip() for item in self.GOOGLE_CLIENT_IDS.split(",") if item.strip()]


# 创建全局配置实例
settings = Settings()
