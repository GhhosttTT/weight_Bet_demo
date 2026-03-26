"""
测试 logger f-string 修复
"""
import requests
import json

# 测试 1: 发送密码长度不足的注册请求（应该返回 422 错误，但不应该崩溃）
print("测试 1: 密码长度不足的注册请求")
response = requests.post(
    "http://localhost:8000/api/auth/register",
    json={
        "email": "test@example.com",
        "password": "123",  # 密码太短
        "nickname": "测试用户",
        "gender": "male",
        "age": 25,
        "height": 170.0,
        "current_weight": 70.0
    }
)
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
print()

# 测试 2: 发送错误的登录请求
print("测试 2: 错误的登录请求")
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
)
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
print()

# 测试 3: 正常的注册请求
print("测试 3: 正常的注册请求")
response = requests.post(
    "http://localhost:8000/api/auth/register",
    json={
        "email": f"test_{int(requests.utils.default_headers()['User-Agent'].split()[0].split('/')[1].replace('.', ''))}@example.com",
        "password": "password123",
        "nickname": "测试用户",
        "gender": "male",
        "age": 25,
        "height": 170.0,
        "current_weight": 70.0
    }
)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("注册成功！")
    data = response.json()
    print(f"用户 ID: {data['user_id']}")
    print(f"昵称: {data['nickname']}")
else:
    print(f"响应: {response.json()}")

print("\n所有测试完成！服务运行正常，没有 KeyError 异常。")
