"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.logger import get_logger
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler
)

logger = get_logger()

# API 标签元数据
tags_metadata = [
    {
        "name": "认证",
        "description": "用户注册、登录、令牌刷新等认证相关操作",
    },
    {
        "name": "用户",
        "description": "用户个人信息管理、统计数据查询",
    },
    {
        "name": "支付",
        "description": "充值、提现、余额查询、交易历史",
    },
    {
        "name": "对赌计划",
        "description": "创建计划、邀请参与、接受/拒绝计划、查询计划详情",
    },
    {
        "name": "邀请",
        "description": "搜索好友、发送邀请、查看邀请列表、接受/拒绝邀请",
    },
    {
        "name": "打卡",
        "description": "每日打卡、上传照片、查看打卡历史、进度统计",
    },
    {
        "name": "结算",
        "description": "自动结算、查询结算详情、争议处理",
    },
    {
        "name": "结算选择",
        "description": "提交结算选择、查询选择状态、选择匹配",
    },
    {
        "name": "通知",
        "description": "推送通知、设备令牌注册",
    },
    {
        "name": "社交",
        "description": "排行榜、评论、鼓励、勋章系统、群组挑战",
    },
    {
        "name": "推荐",
        "description": "个性化健身和饮食推荐",
    },
]

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 减肥对赌 APP API

基于对赌机制的减肥激励应用后端 API。

### 主要功能

* **用户认证**: 注册、登录、第三方登录
* **对赌计划**: 创建减肥计划、邀请好友、接受挑战
* **每日打卡**: 记录体重、上传照片、跟踪进度
* **自动结算**: 计划到期自动结算、资金分配
* **社交互动**: 排行榜、评论、勋章系统

### 认证方式

所有需要认证的 API 都需要在请求头中包含 JWT 令牌:

```
Authorization: Bearer <access_token>
```

### 错误响应格式

所有错误响应都遵循统一格式:

```json
{
  "detail": "错误描述信息"
}
```
    """,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata,
    contact={
        "name": "API Support",
        "email": "support@weightloss-betting.com",
    },
    license_info={
        "name": "MIT",
    },
)

# 注册全局错误处理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 配置 GZip 压缩中间件 (响应压缩)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 配置安全中间件 (最先执行)
app.add_middleware(SecurityMiddleware, enable_csrf=True)

# 配置限流中间件
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置受信任主机
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 生产环境应该配置具体的域名
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Starting {} v{}", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Debug mode: {}", settings.DEBUG)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down {}", settings.APP_NAME)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 导入路由
from app.api import auth, users, payments, betting_plans, check_ins, settlements, settlement_choices, notifications, social, invitations, pending_actions, recommendations
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(payments.router, prefix="/api/payments", tags=["支付"])
app.include_router(betting_plans.router, prefix="/api/betting-plans", tags=["对赌计划"])
app.include_router(invitations.router, prefix="/api", tags=["邀请"])
app.include_router(check_ins.router, prefix="/api", tags=["打卡"])
app.include_router(settlements.router, prefix="/api", tags=["结算"])
app.include_router(settlement_choices.router, prefix="/api", tags=["结算选择"])
app.include_router(notifications.router, prefix="/api", tags=["通知"])
app.include_router(social.router, prefix="/api/social", tags=["社交"])
app.include_router(pending_actions.router, prefix="/api", tags=["邀请"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["推荐"])
