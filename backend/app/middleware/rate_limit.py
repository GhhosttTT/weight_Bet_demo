"""
请求限流中间件
使用 Redis 实现基于用户的请求限流
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.redis_client import get_redis
from app.logger import get_logger
from app.utils.security import decode_token
from typing import Optional, Tuple
import time
import uuid

logger = get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    请求限流中间件
    
    限制每个用户每分钟最多 100 个请求
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 时间窗口: 60 秒
        self.auth_requests_per_minute = 20
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并应用限流
        """
        # 跳过健康检查和文档端点
        if request.url.path in ["/health", "/", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            return await call_next(request)
        
        # 获取用户标识 (从 JWT 令牌或 IP 地址)
        user_id = self._get_user_identifier(request)
        
        # 登录、注册和第三方登录使用更严格的 IP 限流，降低凭证爆破风险。
        request_limit = self._limit_for_path(request.url.path)
        is_allowed, remaining, reset_time = await self._check_rate_limit(user_id, request_limit)
        
        if not is_allowed:
            logger.warning("Rate limit exceeded for user: {}", user_id)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "请求过于频繁,请稍后再试",
                    "retry_after": reset_time
                },
                headers={
                    "X-RateLimit-Limit": str(request_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time)
                }
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流信息到响应头
        response.headers["X-RateLimit-Limit"] = str(request_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_user_identifier(self, request: Request) -> str:
        """
        获取用户标识符
        
        优先使用用户 ID,如果未认证则使用 IP 地址
        """
        # 尝试从请求状态中获取用户 ID（兼容已有认证中间件）
        user_id = getattr(request.state, "user_id", None)
        
        if user_id:
            return f"user:{user_id}"

        # FastAPI 的 Depends 在路由执行阶段才解析，限流中间件无法依赖
        # get_current_user；这里仅解码 JWT 的 subject，不访问数据库。
        authorization = request.headers.get("Authorization", "")
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
            payload = decode_token(token) if token else None
            token_user_id = payload.get("sub") if payload else None
            if token_user_id:
                return f"user:{token_user_id}"
        
        # 如果未认证,使用 IP 地址
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _limit_for_path(self, path: str) -> int:
        if path in ("/api/auth/login", "/api/auth/register", "/api/auth/google", "/api/auth/refresh"):
            return self.auth_requests_per_minute
        return self.requests_per_minute

    async def _check_rate_limit(self, identifier: str, request_limit: Optional[int] = None) -> Tuple[bool, int, int]:
        """
        检查是否超过限流阈值
        
        使用滑动窗口算法
        
        Returns:
            (is_allowed, remaining_requests, reset_time)
        """
        redis = get_redis()
        limit = request_limit or self.requests_per_minute
        current_time = int(time.time())
        window_start = current_time - self.window_size
        
        # Redis key
        key = f"rate_limit:{identifier}"
        
        try:
            # 使用 Redis 管道执行原子操作
            pipe = redis.pipeline()
            
            # 1. 移除窗口外的旧记录
            pipe.zremrangebyscore(key, 0, window_start)
            
            # 2. 统计当前窗口内的请求数
            pipe.zcard(key)
            
            # 3. 添加当前请求
            # member 必须按请求唯一；仅使用秒级时间戳会让同一秒内的请求
            # 相互覆盖，导致限流计数失真。score 仍使用时间戳用于窗口清理。
            request_member = "{}:{}".format(current_time, uuid.uuid4().hex)
            pipe.zadd(key, {request_member: current_time})
            
            # 4. 设置过期时间
            pipe.expire(key, self.window_size + 10)
            
            # 执行管道
            results = pipe.execute()
            
            # 获取当前请求数 (在添加新请求之前)
            request_count = results[1]
            
            # 计算剩余请求数和重置时间
            remaining = max(0, limit - request_count - 1)
            reset_time = current_time + self.window_size
            
            # 判断是否允许请求
            is_allowed = request_count < limit
            
            return is_allowed, remaining, reset_time
            
        except Exception as e:
            logger.error("Rate limit check failed: {}", e)
            # 如果 Redis 出错,允许请求通过 (fail open)
            return True, limit, current_time + self.window_size
