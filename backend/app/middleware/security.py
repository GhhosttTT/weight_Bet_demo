"""
安全防护中间件
实现 SQL 注入防护、XSS 防护、CSRF 保护和输入验证
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger import get_logger
from app.config import settings
import re
import html
from typing import Any, Dict
import json
from urllib.parse import unquote_plus

logger = get_logger()


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    安全防护中间件
    
    提供多层安全防护:
    - SQL 注入防护
    - XSS 防护
    - CSRF 保护
    - 输入验证
    """
    
    # SQL 注入检测模式
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(;\s*(?:DROP|SELECT|INSERT|UPDATE|DELETE|ALTER|CREATE)\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(;.*--)",
        r"(--.*)",
        r"(/\*.*\*/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('.*OR.*'.*=.*')",
    ]
    
    # XSS 检测模式
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<applet[^>]*>",
    ]
    MAX_JSON_BODY_BYTES = 1024 * 1024
    
    def __init__(self, app, enable_csrf: bool = True):
        super().__init__(app)
        self.enable_csrf = enable_csrf
        self.sql_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS]
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求并应用安全检查
        """
        # 跳过健康检查和文档端点
        if request.url.path in ["/health", "/", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            return await call_next(request)
        
        # 1. CSRF 保护 (仅对修改操作)
        if self.enable_csrf and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            if not self._check_csrf_token(request):
                logger.warning("CSRF token validation failed for {}", request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "请求来源未被允许"}
                )
        
        # 2. 验证请求参数
        try:
            # 检查查询参数
            for key, value in request.query_params.items():
                self._validate_input(key, value, "query parameter")

            # Starlette 会把未编码的分号当作查询分隔符，导致恶意片段
            # 被拆成新的键值对；同时检查原始 query string，避免绕过检测。
            raw_query = request.scope.get("query_string", b"").decode(
                "utf-8", errors="replace"
            )
            if raw_query:
                self._validate_input(
                    "__raw_query__", unquote_plus(raw_query), "query string"
                )
            
            # 检查请求体 (如果是 JSON)
            if request.headers.get("content-type", "").startswith("application/json"):
                body = await self._get_request_body(request)
                if body:
                    self._validate_json_input(body)
        
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error("Security validation error: {}", e)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "请求参数验证失败"}
            )
        
        # 3. 处理请求
        response = await call_next(request)
        
        # 4. 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.url.path.startswith("/admin"):
            # 当前同源后台是单文件控制台，脚本和样式内嵌在页面中；
            # 仅对后台页面放行 inline，API 继续使用严格的默认策略。
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _check_csrf_token(self, request: Request) -> bool:
        """
        检查 CSRF token
        
        从请求头或表单中获取 token 并验证
        """
        # 移动端 Bearer 请求通常没有 Origin；浏览器请求有 Origin/Referer 时
        # 必须匹配服务端允许的来源，避免跨站页面直接调用写接口。
        origin = request.headers.get("origin") or request.headers.get("referer", "")
        if not origin:
            return True
        return any(origin == allowed or origin.startswith(f"{allowed}/")
                   for allowed in settings.allowed_origins_list)
    
    async def _get_request_body(self, request: Request) -> Any:
        """
        获取请求体内容，并把已读取的 body 重新提供给下游处理器。

        BaseHTTPMiddleware 读取 receive channel 后不会自动把内容回放给
        路由层；如果不回放，带 JSON body 的请求可能在 TestClient/ASGI
        server 中一直等待剩余请求体。
        """
        try:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_JSON_BODY_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="JSON 请求体不能超过 1MB",
                )

            chunks = []
            total_bytes = 0
            async for chunk in request.stream():
                total_bytes += len(chunk)
                if total_bytes > self.MAX_JSON_BODY_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="JSON 请求体不能超过 1MB",
                    )
                chunks.append(chunk)
            body_bytes = b"".join(chunks)
            async def receive():
                return {
                    "type": "http.request",
                    "body": body_bytes,
                    "more_body": False,
                }
            request._receive = receive
            if body_bytes:
                return json.loads(body_bytes)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to parse request body: {}", e)
        return None
    
    def _validate_input(self, key: str, value: str, input_type: str = "input"):
        """
        验证输入参数
        
        检查 SQL 注入和 XSS 攻击
        """
        if not isinstance(value, str):
            return
        
        # SQL 注入检测
        for pattern in self.sql_patterns:
            if pattern.search(value):
                logger.warning("Potential SQL injection detected in {} '{}': {}", input_type, key, value[:100])
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"检测到非法输入: {key}"
                )
        
        # XSS 检测
        for pattern in self.xss_patterns:
            if pattern.search(value):
                logger.warning("Potential XSS attack detected in {} '{}': {}", input_type, key, value[:100])
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"检测到非法输入: {key}"
                )
    
    def _validate_json_input(self, data: Any, path: str = ""):
        """
        递归验证 JSON 输入
        """
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    self._validate_input(current_path, value, "JSON field")
                elif isinstance(value, (dict, list)):
                    self._validate_json_input(value, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, str):
                    self._validate_input(current_path, item, "JSON array item")
                elif isinstance(item, (dict, list)):
                    self._validate_json_input(item, current_path)
    
    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        清理输出内容,防止 XSS
        
        对 HTML 特殊字符进行转义
        """
        if not isinstance(text, str):
            return text
        return html.escape(text)


def sanitize_html(text: str) -> str:
    """
    清理 HTML 内容
    
    移除潜在的危险标签和属性
    """
    if not isinstance(text, str):
        return text
    
    # 转义 HTML 特殊字符
    text = html.escape(text)
    
    return text
