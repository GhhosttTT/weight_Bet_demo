#!/usr/bin/env python3
"""
测试API
"""
import requests
import json

# 登录获取token
login_data = {
    "email": "1612@qq.com",
    "password": "12345678"
}

print("=== 登录 ===")
response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    auth_result = response.json()
    print(f"User ID: {auth_result['user_id']}")
    print(f"Nickname: {auth_result['nickname']}")
    access_token = auth_result['access_token']
    user_id = auth_result['user_id']
    
    # 获取用户信息
    print("\n=== 获取用户信息 ===")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"http://localhost:8000/api/users/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_info = response.json()
        print(json.dumps(user_info, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")
else:
    print(f"Login failed: {response.text}")
