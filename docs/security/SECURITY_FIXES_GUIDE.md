# 安全漏洞修复指南

本文档提供常见安全漏洞的修复方法和最佳实践。

## 1. 认证和授权修复

### 1.1 密码安全加固

**问题**: 密码存储不安全或密码策略过弱

**修复方法**:

```python
# backend/app/services/auth_service.py

import bcrypt
import re

class AuthService:
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """验证密码强度"""
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        if not re.search(r"[a-z]", password):
            return False, "密码必须包含小写字母"
        
        if not re.search(r"[A-Z]", password):
            return False, "密码必须包含大写字母"
        
        if not re.search(r"\d", password):
            return False, "密码必须包含数字"
        
        # 可选: 检查特殊字符
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        #     return False, "密码必须包含特殊字符"
        
        # 检查常见弱密码
        common_passwords = ["password", "12345678", "qwerty", "abc123"]
        if password.lower() in common_passwords:
            return False, "密码过于简单,请使用更复杂的密码"
        
        return True, "密码强度合格"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """使用 bcrypt 哈希密码"""
        # 使用 cost factor 12 (推荐值)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
```

### 1.2 JWT 令牌安全加固

**问题**: JWT 密钥过弱或令牌配置不当

**修复方法**:

```python
# backend/app/core/security.py

import jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets

class JWTManager:
    # 使用强密钥 (至少256位)
    SECRET_KEY = secrets.token_urlsafe(32)  # 生成随机密钥
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # 令牌黑名单 (使用 Redis)
    token_blacklist = set()
    
    @classmethod
    def create_access_token(cls, user_id: str) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def create_refresh_token(cls, user_id: str) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            # 检查黑名单
            if token in cls.token_blacklist:
                return None
            
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @classmethod
    def revoke_token(cls, token: str):
        """撤销令牌 (添加到黑名单)"""
        cls.token_blacklist.add(token)
        # 在 Redis 中设置过期时间
        # redis_client.setex(f"blacklist:{token}", 86400, "1")
```

### 1.3 权限控制加固

**问题**: 缺少权限验证或越权访问

**修复方法**:

```python
# backend/app/middleware/auth_middleware.py

from fastapi import Request, HTTPException
from functools import wraps

def require_auth(func):
    """认证装饰器"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not token:
            raise HTTPException(status_code=401, detail="未提供认证令牌")
        
        payload = JWTManager.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="无效或过期的令牌")
        
        # 将用户信息添加到请求上下文
        request.state.user_id = payload["user_id"]
        
        return await func(request, *args, **kwargs)
    
    return wrapper

def require_owner(resource_user_id_param: str):
    """资源所有者验证装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            current_user_id = request.state.user_id
            resource_user_id = kwargs.get(resource_user_id_param)
            
            if current_user_id != resource_user_id:
                raise HTTPException(status_code=403, detail="无权访问此资源")
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator

# 使用示例
@app.get("/api/users/{user_id}")
@require_auth
@require_owner("user_id")
async def get_user(request: Request, user_id: str):
    # 只有用户本人可以访问
    pass
```

## 2. 注入攻击修复

### 2.1 SQL 注入防护

**问题**: 使用字符串拼接构建 SQL 查询

**修复方法**:

```python
# 错误示例 (不要这样做!)
def get_user_by_email_unsafe(email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)

# 正确示例 1: 使用参数化查询
def get_user_by_email_safe(email: str):
    query = "SELECT * FROM users WHERE email = %s"
    return db.execute(query, (email,))

# 正确示例 2: 使用 ORM (推荐)
from sqlalchemy import select

def get_user_by_email_orm(email: str):
    stmt = select(User).where(User.email == email)
    return db.session.execute(stmt).scalar_one_or_none()
```

### 2.2 NoSQL 注入防护

**问题**: MongoDB 查询未验证输入

**修复方法**:

```python
# 错误示例
def find_user_unsafe(email):
    return db.users.find_one({"email": email})
    # 如果 email = {"$gt": ""}, 会返回所有用户

# 正确示例: 验证输入类型
def find_user_safe(email: str):
    if not isinstance(email, str):
        raise ValueError("Email must be a string")
    
    # 转义特殊字符
    email = email.replace("$", "\\$")
    
    return db.users.find_one({"email": email})
```

### 2.3 命令注入防护

**问题**: 直接执行用户输入的命令

**修复方法**:

```python
import subprocess
import shlex

# 错误示例 (不要这样做!)
def process_file_unsafe(filename: str):
    os.system(f"convert {filename} output.jpg")

# 正确示例: 使用参数列表
def process_file_safe(filename: str):
    # 验证文件名
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        raise ValueError("Invalid filename")
    
    # 使用参数列表而不是字符串
    subprocess.run(
        ["convert", filename, "output.jpg"],
        check=True,
        timeout=30
    )
```

## 3. XSS 防护

### 3.1 输出转义

**问题**: 用户输入未转义直接输出

**修复方法**:

```python
# backend/app/utils/sanitizer.py

import html
import bleach

def sanitize_html(content: str) -> str:
    """清理 HTML 内容"""
    # 允许的标签和属性
    allowed_tags = ['p', 'br', 'strong', 'em', 'u']
    allowed_attrs = {}
    
    # 使用 bleach 清理
    clean_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    
    return clean_content

def escape_html(content: str) -> str:
    """转义 HTML 特殊字符"""
    return html.escape(content)

# 使用示例
@app.post("/api/comments")
async def create_comment(content: str):
    # 清理用户输入
    safe_content = sanitize_html(content)
    
    # 保存到数据库
    comment = Comment(content=safe_content)
    db.session.add(comment)
    db.session.commit()
    
    return {"content": safe_content}
```

### 3.2 Content Security Policy

**修复方法**:

```python
# backend/app/middleware/security_headers.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.example.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.example.com; "
            "frame-ancestors 'none';"
        )
        
        # 其他安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

# 添加中间件
app.add_middleware(SecurityHeadersMiddleware)
```

## 4. CSRF 防护

**问题**: 缺少 CSRF 保护

**修复方法**:

```python
# backend/app/middleware/csrf_middleware.py

import secrets
from fastapi import Request, HTTPException

class CSRFMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # 对状态改变操作验证 CSRF 令牌
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                csrf_token = request.headers.get("X-CSRF-Token")
                session_token = request.session.get("csrf_token")
                
                if not csrf_token or csrf_token != session_token:
                    raise HTTPException(status_code=403, detail="CSRF token missing or invalid")
        
        await self.app(scope, receive, send)

# 生成 CSRF 令牌
@app.get("/api/csrf-token")
async def get_csrf_token(request: Request):
    token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = token
    return {"csrf_token": token}
```

## 5. 文件上传安全

**问题**: 文件上传未验证或存储不安全

**修复方法**:

```python
# backend/app/utils/file_upload.py

import os
import magic
from werkzeug.utils import secure_filename

class FileUploadValidator:
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def validate_file(file) -> tuple[bool, str]:
        """验证上传的文件"""
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > FileUploadValidator.MAX_FILE_SIZE:
            return False, "文件大小超过限制"
        
        # 检查文件扩展名
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext not in FileUploadValidator.ALLOWED_EXTENSIONS:
            return False, "不支持的文件类型"
        
        # 检查文件 MIME 类型 (使用 magic number)
        file_content = file.read(1024)
        file.seek(0)
        
        mime = magic.from_buffer(file_content, mime=True)
        if not mime.startswith('image/'):
            return False, "文件内容不是有效的图片"
        
        return True, "验证通过"
    
    @staticmethod
    def save_file(file, upload_dir: str) -> str:
        """安全保存文件"""
        # 生成随机文件名
        ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename = f"{secrets.token_urlsafe(16)}.{ext}"
        
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file.read())
        
        return filename

# 使用示例
@app.post("/api/check-ins/{check_in_id}/photo")
async def upload_photo(check_in_id: str, file: UploadFile):
    # 验证文件
    is_valid, message = FileUploadValidator.validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # 保存文件
    filename = FileUploadValidator.save_file(file, "uploads/check_ins")
    
    # 更新数据库
    check_in = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
    check_in.photo_url = f"/uploads/check_ins/{filename}"
    db.commit()
    
    return {"photo_url": check_in.photo_url}
```

## 6. 限流实现

**问题**: 缺少 API 限流保护

**修复方法**:

```python
# backend/app/middleware/rate_limit.py

import time
from collections import defaultdict
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        minute_ago = now - 60
        
        # 清理过期的请求记录
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > minute_ago
        ]
        
        # 检查请求数量
        if len(self.requests[key]) >= self.requests_per_minute:
            return False
        
        # 记录新请求
        self.requests[key].append(now)
        return True

# 使用 Redis 实现 (推荐用于生产环境)
import redis

class RedisRateLimiter:
    def __init__(self, redis_client, requests_per_minute: int = 100):
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute
    
    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        pipe = self.redis.pipeline()
        now = time.time()
        
        # 使用 sorted set 存储请求时间戳
        pipe.zadd(f"rate_limit:{key}", {now: now})
        pipe.zremrangebyscore(f"rate_limit:{key}", 0, now - 60)
        pipe.zcard(f"rate_limit:{key}")
        pipe.expire(f"rate_limit:{key}", 60)
        
        results = pipe.execute()
        request_count = results[2]
        
        return request_count <= self.requests_per_minute

# 中间件
rate_limiter = RedisRateLimiter(redis_client)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 使用用户 ID 或 IP 作为限流键
    user_id = request.state.get("user_id", request.client.host)
    
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁,请稍后再试",
            headers={"Retry-After": "60"}
        )
    
    response = await call_next(request)
    return response
```

## 7. 日志安全

**问题**: 日志中包含敏感信息

**修复方法**:

```python
# backend/app/utils/logger.py

import logging
import re

class SensitiveDataFilter(logging.Filter):
    """过滤日志中的敏感数据"""
    
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'password=***'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'token=***'),
        (r'api_key["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'api_key=***'),
        (r'\b\d{16}\b', '****-****-****-****'),  # 信用卡号
        (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),  # SSN
    ]
    
    def filter(self, record):
        message = record.getMessage()
        
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        record.msg = message
        return True

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())
```

## 8. 移动端安全加固

### 8.1 Android 证书固定

```kotlin
// android/app/src/main/java/com/weightloss/betting/network/CertificatePinner.kt

import okhttp3.CertificatePinner
import okhttp3.OkHttpClient

object NetworkClient {
    private val certificatePinner = CertificatePinner.Builder()
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
        .build()
    
    val client = OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()
}
```

### 8.2 iOS 证书固定

```swift
// ios/WeightLossBetting/Network/CertificatePinner.swift

import Foundation

class CertificatePinner: NSObject, URLSessionDelegate {
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        // 验证证书
        let policies = [SecPolicyCreateSSL(true, "api.example.com" as CFString)]
        SecTrustSetPolicies(serverTrust, policies as CFTypeRef)
        
        var result: SecTrustResultType = .invalid
        SecTrustEvaluate(serverTrust, &result)
        
        if result == .unspecified || result == .proceed {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

## 安全修复优先级

### 高优先级 (立即修复)
1. SQL 注入漏洞
2. 认证绕过
3. 敏感数据泄露
4. 远程代码执行
5. 支付安全漏洞

### 中优先级 (1周内修复)
1. XSS 漏洞
2. CSRF 漏洞
3. 权限控制问题
4. 会话管理问题
5. 文件上传漏洞

### 低优先级 (1个月内修复)
1. 信息泄露
2. 配置问题
3. 日志问题
4. 性能问题

## 修复验证

修复完成后,必须进行以下验证:

1. **代码审查**: 由其他开发人员审查修复代码
2. **安全测试**: 重新执行渗透测试
3. **回归测试**: 确保修复没有破坏现有功能
4. **性能测试**: 确保修复没有影响性能
5. **文档更新**: 更新安全文档和最佳实践

## 持续安全

1. **定期审计**: 每季度进行安全审计
2. **依赖更新**: 每月更新依赖库
3. **安全培训**: 定期进行安全培训
4. **漏洞监控**: 订阅安全公告
5. **应急响应**: 建立安全事件响应流程
