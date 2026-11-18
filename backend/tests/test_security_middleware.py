"""
安全中间件单元测试
测试限流、输入验证和安全防护功能
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.redis_client import get_redis
from app.config import settings
from unittest.mock import Mock, patch
import time


# 创建测试应用
def create_test_app():
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"message": "success", "data": data}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


class TestRateLimitMiddleware:
    """测试限流中间件"""

    @pytest.fixture(autouse=True)
    def clear_rate_limit_state(self):
        """隔离测试用例，避免共享 Redis 中的 IP 计数。"""
        get_redis().delete("rate_limit:ip:testclient")
    
    def test_rate_limit_allows_requests_within_limit(self):
        """测试限流允许限制内的请求"""
        app = create_test_app()
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)
        client = TestClient(app)
        
        # 发送 5 个请求,应该都成功
        for i in range(5):
            response = client.get("/test")
            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
    
    def test_rate_limit_blocks_requests_over_limit(self):
        """测试限流阻止超过限制的请求"""
        app = create_test_app()
        app.add_middleware(RateLimitMiddleware, requests_per_minute=5)
        client = TestClient(app)
        
        # 发送 5 个请求,应该都成功
        for i in range(5):
            response = client.get("/test")
            assert response.status_code == 200
        
        # 第 6 个请求应该被限流
        response = client.get("/test")
        assert response.status_code == 429
        assert "retry_after" in response.json() or "Retry-After" in response.headers
    
    def test_rate_limit_skips_health_check(self):
        """测试限流跳过健康检查端点"""
        app = create_test_app()
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2)
        client = TestClient(app)
        
        # 健康检查端点不应该被限流
        for i in range(10):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_rate_limit_headers_present(self):
        """测试限流响应头存在"""
        app = create_test_app()
        app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "100"

    def test_rate_limit_uses_authenticated_subject(self):
        app = create_test_app()
        middleware = RateLimitMiddleware(app)
        request = Mock()
        request.state.user_id = None
        request.headers = {"Authorization": "Bearer valid-token"}

        with patch("app.middleware.rate_limit.decode_token", return_value={"sub": "user-123"}):
            assert middleware._get_user_identifier(request) == "user:user-123"

    def test_auth_paths_use_stricter_limit(self):
        app = create_test_app()
        middleware = RateLimitMiddleware(app, requests_per_minute=100)
        assert middleware._limit_for_path("/api/auth/login") == 20
        assert middleware._limit_for_path("/api/auth/google") == 20
        assert middleware._limit_for_path("/api/payments/charge/intent") == 100


class TestSecurityMiddleware:
    """测试安全中间件"""
    
    def test_security_headers_added(self):
        """测试安全响应头被添加"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
    
    def test_sql_injection_detection_in_query_params(self):
        """测试查询参数中的 SQL 注入检测"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试 SQL 注入模式
        malicious_queries = [
            "1' OR '1'='1",
            "admin'--",
            "1; DROP TABLE users",
            "UNION SELECT * FROM users",
        ]
        
        for query in malicious_queries:
            response = client.get(f"/test?input={query}")
            assert response.status_code == 400
            assert "非法输入" in response.json()["detail"]
    
    def test_xss_detection_in_query_params(self):
        """测试查询参数中的 XSS 检测"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试 XSS 模式
        malicious_queries = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<iframe src='evil.com'></iframe>",
            "<img onerror='alert(1)' src='x'>",
        ]
        
        for query in malicious_queries:
            response = client.get(f"/test?input={query}")
            assert response.status_code == 400
            assert "非法输入" in response.json()["detail"]
    
    def test_sql_injection_detection_in_json_body(self):
        """测试 JSON 请求体中的 SQL 注入检测"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试 SQL 注入
        malicious_data = {
            "username": "admin' OR '1'='1",
            "password": "password"
        }
        
        response = client.post("/test", json=malicious_data)
        assert response.status_code == 400
        assert "非法输入" in response.json()["detail"]
    
    def test_xss_detection_in_json_body(self):
        """测试 JSON 请求体中的 XSS 检测"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试 XSS
        malicious_data = {
            "comment": "<script>alert('xss')</script>",
            "title": "Test"
        }
        
        response = client.post("/test", json=malicious_data)
        assert response.status_code == 400
        assert "非法输入" in response.json()["detail"]
    
    def test_nested_json_validation(self):
        """测试嵌套 JSON 的验证"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试嵌套对象中的恶意输入
        malicious_data = {
            "user": {
                "name": "John",
                "bio": "<script>alert('xss')</script>"
            }
        }
        
        response = client.post("/test", json=malicious_data)
        assert response.status_code == 400
    
    def test_array_validation(self):
        """测试数组中的验证"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试数组中的恶意输入
        malicious_data = {
            "tags": ["tag1", "tag2", "'; DROP TABLE users--"]
        }
        
        response = client.post("/test", json=malicious_data)
        assert response.status_code == 400
    
    def test_safe_input_allowed(self):
        """测试安全输入被允许"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 测试正常输入
        safe_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "bio": "I love coding!"
        }
        
        response = client.post("/test", json=safe_data)
        assert response.status_code == 200

    def test_cross_site_write_is_rejected(self):
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)

        response = client.post(
            "/test",
            json={"username": "john_doe"},
            headers={"Origin": "https://evil.example.com"},
        )

        assert response.status_code == 403

    def test_allowed_origin_write_is_accepted(self, monkeypatch):
        monkeypatch.setattr(settings, "ALLOWED_ORIGINS", "https://app.example.com")
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)

        response = client.post(
            "/test",
            json={"username": "john_doe"},
            headers={"Origin": "https://app.example.com"},
        )

        assert response.status_code == 200
    
    def test_health_check_bypasses_security(self):
        """测试健康检查端点绕过安全检查"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200


class TestCombinedMiddleware:
    """测试组合中间件"""
    
    def test_rate_limit_and_security_together(self):
        """测试限流和安全中间件一起工作"""
        app = create_test_app()
        app.add_middleware(SecurityMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)
        client = TestClient(app)
        
        # 正常请求应该通过
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-Content-Type-Options" in response.headers
    
    def test_security_blocks_before_rate_limit(self):
        """测试安全检查在限流之前执行"""
        app = create_test_app()
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        # 恶意请求应该被安全中间件阻止,不消耗限流配额
        for i in range(5):
            response = client.get("/test?input=<script>alert('xss')</script>")
            assert response.status_code == 400
        
        # 正常请求应该仍然可以通过
        response = client.get("/test")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
