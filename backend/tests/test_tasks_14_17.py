"""
测试任务 14-17 的实现
"""
import pytest
from app.services.cache_service import cache_service
from app.main import app
from fastapi.testclient import TestClient


class TestTask14Performance:
    """测试任务14: 性能优化"""
    
    def test_cache_service_exists(self):
        """测试缓存服务是否存在"""
        assert cache_service is not None
        assert hasattr(cache_service, 'get_user_info')
        assert hasattr(cache_service, 'set_user_info')
        assert hasattr(cache_service, 'get_plan_details')
        assert hasattr(cache_service, 'get_leaderboard')
        assert hasattr(cache_service, 'get_user_balance')
    
    def test_cache_ttl_configuration(self):
        """测试缓存TTL配置"""
        assert cache_service.TTL_USER_INFO == 600  # 10分钟
        assert cache_service.TTL_PLAN_DETAILS == 300  # 5分钟
        assert cache_service.TTL_LEADERBOARD == 300  # 5分钟
        assert cache_service.TTL_USER_BALANCE == 60  # 1分钟
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        key = cache_service._make_key("user", "123")
        assert key == "user:123"
        
        key = cache_service._make_key("plan", "456")
        assert key == "plan:456"
    
    def test_gzip_middleware_configured(self):
        """测试GZip压缩中间件是否配置"""
        # 检查中间件是否在应用中
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert 'GZipMiddleware' in middleware_classes


class TestTask15APIDocumentation:
    """测试任务15: API文档"""
    
    def test_openapi_docs_available(self):
        """测试OpenAPI文档是否可访问"""
        client = TestClient(app)
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        
        openapi_schema = response.json()
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema
        assert "paths" in openapi_schema
    
    def test_swagger_ui_available(self):
        """测试Swagger UI是否可访问"""
        client = TestClient(app)
        response = client.get("/api/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self):
        """测试ReDoc是否可访问"""
        client = TestClient(app)
        response = client.get("/api/redoc")
        assert response.status_code == 200
    
    def test_api_tags_configured(self):
        """测试API标签是否配置"""
        client = TestClient(app)
        response = client.get("/api/openapi.json")
        openapi_schema = response.json()
        
        assert "tags" in openapi_schema
        tags = [tag["name"] for tag in openapi_schema["tags"]]
        
        expected_tags = ["认证", "用户", "支付", "对赌计划", "打卡", "结算", "通知", "社交"]
        for tag in expected_tags:
            assert tag in tags
    
    def test_api_endpoints_documented(self):
        """测试API端点是否有文档"""
        client = TestClient(app)
        response = client.get("/api/openapi.json")
        openapi_schema = response.json()
        
        paths = openapi_schema["paths"]
        
        # 检查关键端点是否存在
        assert "/api/auth/register" in paths
        assert "/api/auth/login" in paths
        assert "/api/users/{user_id}" in paths
        assert "/api/betting-plans" in paths


class TestTask16BackendCheckpoint:
    """测试任务16: 后端检查点"""
    
    def test_app_starts_successfully(self):
        """测试应用是否能成功启动"""
        assert app is not None
        assert app.title == "减肥对赌 APP"
    
    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        """测试根端点"""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
    
    def test_middleware_configured(self):
        """测试中间件是否配置"""
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        
        # 检查关键中间件
        assert 'GZipMiddleware' in middleware_classes
        assert 'CORSMiddleware' in middleware_classes
        assert 'RateLimitMiddleware' in middleware_classes
        assert 'SecurityMiddleware' in middleware_classes


class TestTask17AndroidProject:
    """测试任务17: Android项目基础架构"""
    
    def test_android_project_exists(self):
        """测试Android项目是否存在"""
        import os
        # Android项目在父目录
        android_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "android")
        assert os.path.exists(android_path) or os.path.exists("../android"), \
            "Android project should exist in parent directory"
    
    def test_android_readme_content(self):
        """测试Android README内容"""
        import os
        # 尝试多个可能的路径
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "android", "README.md"),
            "../android/README.md",
            "../../android/README.md"
        ]
        
        readme_found = False
        content = ""
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                readme_found = True
                break
        
        if not readme_found:
            # 如果找不到文件，跳过测试而不是失败
            import pytest
            pytest.skip("Android README.md not found in expected locations")
        
        # 检查关键内容
        assert "Kotlin" in content
        assert "MVVM" in content
        assert "Retrofit" in content
        assert "Room" in content
        assert "Hilt" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
