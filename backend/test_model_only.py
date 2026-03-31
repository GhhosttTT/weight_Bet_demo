#!/usr/bin/env python3
"""
简单的模型侧接口测试
"""
import httpx
import asyncio
import json

MODEL_URL = "http://192.168.1.108:8000"

async def test_model_direct():
    """直接测试模型侧接口"""
    print("=" * 60)
    print("模型侧接口测试")
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
    
    print(f"\n请求地址: {MODEL_URL}/api/recommend")
    print(f"请求体: {json.dumps(test_request, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        print("正在连接模型侧...")
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{MODEL_URL}/api/recommend",
                json=test_request,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n状态码: {response.status_code}")
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
    except httpx.ConnectError as e:
        print(f"\n✗ 连接模型侧失败: {e}")
        print(f"  请确认:")
        print(f"  1. 模型侧服务是否已启动")
        print(f"  2. 模型侧地址是否正确: {MODEL_URL}")
        print(f"  3. 防火墙是否阻止了连接")
        return False
    except httpx.TimeoutException:
        print(f"\n✗ 连接模型侧超时")
        print(f"  请确认模型侧服务是否正在运行")
        return False
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_model_direct())
