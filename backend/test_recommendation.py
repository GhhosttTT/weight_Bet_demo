#!/usr/bin/env python3
"""
推荐功能联调测试脚本
"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:9191"
MODEL_URL = "http://192.168.1.108:8000"

# 测试账号
TEST_EMAIL = "test1@qq.com"
TEST_PASSWORD = "12345678"

access_token = None


async def login():
    """登录获取token"""
    print("\n" + "=" * 60)
    print("1. 登录测试")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            global access_token
            access_token = data.get("access_token")
            print(f"\n✓ 登录成功！")
            print(f"  Access Token: {access_token[:50]}...")
            return True
        else:
            print(f"\n✗ 登录失败")
            return False


async def test_get_recommendation():
    """测试获取推荐"""
    print("\n" + "=" * 60)
    print("2. 测试获取推荐 (GET /api/recommendations/)")
    print("=" * 60)
    
    if not access_token:
        print("✗ 未登录，跳过测试")
        return False
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/recommendations/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"状态码: {response.status_code}")
        try:
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except:
            print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print(f"\n✓ 获取推荐成功！")
            return True
        else:
            print(f"\n✗ 获取推荐失败")
            return False


async def test_refresh_recommendation():
    """测试刷新推荐"""
    print("\n" + "=" * 60)
    print("3. 测试刷新推荐 (POST /api/recommendations/refresh)")
    print("=" * 60)
    
    if not access_token:
        print("✗ 未登录，跳过测试")
        return False
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/recommendations/refresh",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"状态码: {response.status_code}")
        try:
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except:
            print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print(f"\n✓ 刷新推荐成功！")
            return True
        else:
            print(f"\n✗ 刷新推荐失败")
            return False


async def test_model_direct():
    """直接测试模型侧接口"""
    print("\n" + "=" * 60)
    print("4. 直接测试模型侧接口 (POST /api/recommend)")
    print("=" * 60)
    
    test_request = {
        "user_profile": {
            "user_id": "test-user",
            "age": 25,
            "gender": "male",
            "height": 175.0,
            "current_weight": 70.0,
            "target_weight": 65.0,
            "initial_weight": 75.0
        },
        "check_in_records": [],
        "request_type": "login"
    }
    
    print(f"请求地址: {MODEL_URL}/api/recommend")
    print(f"请求体: {json.dumps(test_request, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{MODEL_URL}/api/recommend",
                json=test_request,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            try:
                print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            except:
                print(f"响应: {response.text}")
            
            if response.status_code == 200:
                print(f"\n✓ 模型侧接口正常！")
                return True
            else:
                print(f"\n✗ 模型侧接口返回错误")
                return False
    except Exception as e:
        print(f"✗ 连接模型侧失败: {e}")
        print(f"  请确认模型侧服务是否已启动，地址是否正确: {MODEL_URL}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("减肥对赌 APP - 推荐功能联调测试")
    print("=" * 60)
    print(f"后端地址: {BASE_URL}")
    print(f"模型侧地址: {MODEL_URL}")
    print(f"测试账号: {TEST_EMAIL}")
    
    results = []
    
    # 1. 测试模型侧直接连接
    results.append(("模型侧接口测试", await test_model_direct()))
    
    # 2. 登录
    results.append(("登录测试", await login()))
    
    # 3. 测试获取推荐
    results.append(("获取推荐测试", await test_get_recommendation()))
    
    # 4. 测试刷新推荐
    results.append(("刷新推荐测试", await test_refresh_recommendation()))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
