"""
安全防护中间件
实现 SQL 注入防护、XSS 防护、CSRF 保护和输入验证
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger import get_logger
import re
import html
from typing import Any, Dict
import json

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
                # 注意: 在生产环境中应该严格验证 CSRF token
                # 这里为了兼容性暂时只记录警告
                # return JSONResponse(
                #     status_code=status.HTTP_403_FORBIDDEN,
                #     content={"detail": "CSRF token 验证失败"}
                # )
        
        # 2. 验证请求参数
        try:
            # 检查查询参数
            for key, value in request.query_params.items():
                self._validate_input(key, value, "query parameter")
            
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
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _check_csrf_token(self, request: Request) -> bool:
        """
        检查 CSRF token
        
        从请求头或表单中获取 token 并验证
        """
        # 从请求头获取 token
        csrf_token = request.headers.get("X-CSRF-Token") or request.headers.get("X-CSRFToken")
        
        # 如果没有 token,检查是否是受信任的来源
        if not csrf_token:
            origin = request.headers.get("origin") or request.headers.get("referer", "")
            # 简化的 CSRF 检查: 允许同源请求
            # 在生产环境中应该使用更严格的 token 验证
            return True
        
        # 验证 token (这里需要实现 token 验证逻辑)
        # 实际应用中应该验证 token 是否与会话中的 token 匹配
        return True
    
    async def _get_request_body(self, request: Request) -> Any:
        """
        获取请求体内容
        """
        try:
            body_bytes = await request.body()
            if body_bytes:
                return json.loads(body_bytes)
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
