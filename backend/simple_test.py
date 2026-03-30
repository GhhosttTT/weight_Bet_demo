#!/usr/bin/env python3
"""简单的后端测试脚本"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  测试后端导入...")
print("=" * 60)

try:
    from app.main import app
    print("✓ app.main 导入成功")
    
    from fastapi.testclient import TestClient
    client = TestClient(app)
    print("✓ TestClient 创建成功")
    
    print("\n" + "=" * 60)
    print("  测试 API 端点...")
    print("=" * 60)
    
    response = client.get("/")
    print(f"✓ GET / - 状态码: {response.status_code}")
    print(f"  响应: {response.json()}")
    
    response = client.get("/health")
    print(f"✓ GET /health - 状态码: {response.status_code}")
    print(f"  响应: {response.json()}")
    
    print("\n" + "=" * 60)
    print("  所有测试通过！现在启动服务器...")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务器")
    print("\nAPI 文档: http://localhost:8000/api/docs")
    print("ReDoc:    http://localhost:8000/api/redoc")
    print()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
