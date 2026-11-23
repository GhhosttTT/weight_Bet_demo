"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional
import os
import re


# Payment and payout services currently convert user-facing decimal amounts to
# minor units by multiplying by 100.  Keep currencies with Stripe's zero-
# decimal/special payout rules out of this path until the amount conversion is
# made currency-aware.
STRIPE_ZERO_DECIMAL_CURRENCIES = {
    "bif", "clp", "djf", "gnf", "jpy", "kmf", "krw", "mga", "pyg",
    "rwf", "ugx", "vnd", "vuv", "xaf", "xof", "xpf",
}
STRIPE_SPECIAL_PAYOUT_CURRENCIES = {"huf", "twd"}


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
    # 短时 access token 降低泄露后的可利用窗口，续期通过 refresh token 完成。
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    # 迁移旧版本 JWT。生产部署必须关闭，当前默认值仅兼容本地旧测试/客户端。
    ALLOW_LEGACY_ACCESS_TOKENS: bool = True
    
    # Stripe 配置
    STRIPE_SECRET_KEY: str = "sk_test_dummy"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_dummy"
    STRIPE_WEBHOOK_SECRET: str = "whsec_test_dummy"
    PAYMENT_PROVIDER: str = "demo"
    STRIPE_CURRENCY: str = "cny"
    STRIPE_CONNECT_COUNTRY: str = "US"
    STRIPE_CONNECT_RETURN_URL: str = "http://localhost:3000/payment/connect/complete"
    STRIPE_CONNECT_REFRESH_URL: str = "http://localhost:3000/payment/connect/retry"
    
    # Firebase 配置
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"
    FCM_PROJECT_ID: str = ""

    # APNs Token Authentication 配置。私钥只从部署环境读取，不提交到仓库。
    APNS_KEY_ID: str = ""
    APNS_TEAM_ID: str = ""
    APNS_PRIVATE_KEY_PATH: str = ""
    APNS_BUNDLE_ID: str = ""
    APNS_USE_SANDBOX: bool = False

    # Google Identity Services。多个客户端 ID 用逗号分隔，生产环境必须配置。
    GOOGLE_CLIENT_IDS: str = ""
    
    # 推荐模型配置
    RECOMMENDATION_MODEL_URL: str = "http://localhost:8001"
    
    # 应用配置
    APP_NAME: str = "减肥对赌 APP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ALLOWED_HOSTS: str = "*"
    
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
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    @property
    def google_client_ids_list(self) -> List[str]:
        """返回启用的 Google OAuth Client ID 列表。"""
        return [item.strip() for item in self.GOOGLE_CLIENT_IDS.split(",") if item.strip()]


def validate_runtime_configuration(current: Settings = None) -> None:
    """拒绝生产环境中的开发占位配置和不安全数据库。"""
    runtime = current or settings
    environment = runtime.ENVIRONMENT.strip().lower()
    is_production = environment in {"production", "prod", "staging"}
    payment_provider = runtime.PAYMENT_PROVIDER.strip().lower()
    if runtime.DATABASE_URL.lower().startswith("sqlite") and not is_production:
        return

    errors = []
    if is_production and runtime.DATABASE_URL.lower().startswith("sqlite"):
        errors.append("生产环境不能使用 SQLite，必须配置 PostgreSQL 等生产数据库")
    if not runtime.SECRET_KEY or runtime.SECRET_KEY == "test-secret-key-for-development" or len(runtime.SECRET_KEY) < 32:
        errors.append("SECRET_KEY 必须是至少 32 位的生产密钥")
    if is_production and runtime.ALLOW_LEGACY_ACCESS_TOKENS:
        errors.append("生产环境必须关闭 ALLOW_LEGACY_ACCESS_TOKENS")
    if is_production and not 5 <= runtime.ACCESS_TOKEN_EXPIRE_MINUTES <= 60:
        errors.append("生产环境 ACCESS_TOKEN_EXPIRE_MINUTES 必须在 5 到 60 分钟之间")
    if "localhost" in runtime.ALLOWED_ORIGINS or "127.0.0.1" in runtime.ALLOWED_ORIGINS:
        errors.append("ALLOWED_ORIGINS 不能使用本地开发地址")
    if not runtime.ALLOWED_HOSTS or "*" in runtime.allowed_hosts_list:
        errors.append("ALLOWED_HOSTS 必须配置正式域名")
    if not runtime.google_client_ids_list:
        errors.append("GOOGLE_CLIENT_IDS 必须配置，避免生产环境出现不可用的 Google 登录按钮")
    redis_url = (runtime.REDIS_URL or "").strip().lower()
    if is_production and (not redis_url or redis_url == "redis://localhost:6379/0"):
        errors.append("生产环境必须配置独立的 Redis 地址，不能使用默认本地 Redis")
    if payment_provider not in {"demo", "stripe"}:
        errors.append("PAYMENT_PROVIDER 只能配置为 demo 或 stripe")
    if is_production and payment_provider != "stripe":
        errors.append("生产环境必须配置 PAYMENT_PROVIDER=stripe，禁止使用演示支付")
    if payment_provider == "stripe":
        if not re.fullmatch(r"[a-z]{3}", runtime.STRIPE_CURRENCY or ""):
            errors.append("STRIPE_CURRENCY 必须是小写三位 ISO 4217 币种代码")
        elif runtime.STRIPE_CURRENCY.lower() in (
            STRIPE_ZERO_DECIMAL_CURRENCIES | STRIPE_SPECIAL_PAYOUT_CURRENCIES
        ):
            errors.append(
                "当前支付金额换算按两位小数实现，暂不支持 Stripe 零小数或特殊出款币种"
            )
        if not re.fullmatch(r"[A-Z]{2}", runtime.STRIPE_CONNECT_COUNTRY or ""):
            errors.append("STRIPE_CONNECT_COUNTRY 必须是大写两位 ISO 3166-1 国家代码")
        if not runtime.STRIPE_SECRET_KEY or runtime.STRIPE_SECRET_KEY.endswith("dummy"):
            errors.append("STRIPE_SECRET_KEY 尚未配置")
        if not runtime.STRIPE_WEBHOOK_SECRET or runtime.STRIPE_WEBHOOK_SECRET.endswith("dummy"):
            errors.append("STRIPE_WEBHOOK_SECRET 尚未配置")
        if not runtime.STRIPE_CONNECT_RETURN_URL.lower().startswith("https://"):
            errors.append("STRIPE_CONNECT_RETURN_URL 必须使用 HTTPS")
        if not runtime.STRIPE_CONNECT_REFRESH_URL.lower().startswith("https://"):
            errors.append("STRIPE_CONNECT_REFRESH_URL 必须使用 HTTPS")
    if errors:
        raise RuntimeError("生产配置校验失败: " + "；".join(errors))


# 创建全局配置实例
settings = Settings()
