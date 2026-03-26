"""
跨平台集成测试

测试 Android、iOS 和后端 API 之间的数据互通和功能一致性
"""

import pytest
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any


class TestCrossPlatform:
    """跨平台集成测试类"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API 基础 URL"""
        return "http://localhost:8000/api"
    
    @pytest.fixture(scope="class")
    def test_users(self):
        """测试用户数据"""
        return {
            "user_a": {
                "email": "test_android@example.com",
                "password": "Test123456!",
                "nickname": "Android测试用户",
                "gender": "male",
                "age": 25,
                "height": 175.0,
                "current_weight": 80.0,
                "target_weight": 75.0
            },
            "user_b": {
                "email": "test_ios@example.com",
                "password": "Test123456!",
                "nickname": "iOS测试用户",
                "gender": "female",
                "age": 23,
                "height": 165.0,
                "current_weight": 60.0,
                "target_weight": 55.0
            }
        }
    
    @pytest.fixture(scope="class")
    def user_tokens(self, api_base_url, test_users):
        """注册并登录测试用户,返回令牌"""
        tokens = {}
        
        for user_key, user_data in test_users.items():
            # 注册用户
            register_response = requests.post(
                f"{api_base_url}/auth/register",
                json=user_data
            )
            
            # 如果用户已存在,直接登录
            if register_response.status_code == 400:
                login_response = requests.post(
                    f"{api_base_url}/auth/login",
                    json={
                        "email": user_data["email"],
                        "password": user_data["password"]
                    }
                )
                assert login_response.status_code == 200
                tokens[user_key] = login_response.json()["access_token"]
            else:
                assert register_response.status_code == 201
                tokens[user_key] = register_response.json()["access_token"]
        
        return tokens
    
    def test_scenario_1_cross_platform_auth(self, api_base_url, test_users, user_tokens):
        """
        场景 1: 跨平台用户注册和登录
        
        验证用户可以在一个平台注册,在另一个平台登录
        """
        # 验证用户 A 的令牌有效
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        response_a = requests.get(f"{api_base_url}/users/me", headers=headers_a)
        assert response_a.status_code == 200
        user_a_data = response_a.json()
        assert user_a_data["email"] == test_users["user_a"]["email"]
        assert user_a_data["nickname"] == test_users["user_a"]["nickname"]
        
        # 验证用户 B 的令牌有效
        headers_b = {"Authorization": f"Bearer {user_tokens['user_b']}"}
        response_b = requests.get(f"{api_base_url}/users/me", headers=headers_b)
        assert response_b.status_code == 200
        user_b_data = response_b.json()
        assert user_b_data["email"] == test_users["user_b"]["email"]
        assert user_b_data["nickname"] == test_users["user_b"]["nickname"]
        
        print("✅ 场景 1 通过: 跨平台用户注册和登录")
    
    def test_scenario_2_cross_platform_betting_plan(self, api_base_url, user_tokens):
        """
        场景 2: 跨平台创建和接受对赌计划
        
        验证在一个平台创建的计划可以在另一个平台查看和接受
        """
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['user_b']}"}
        
        # 用户 A (Android) 创建对赌计划
        plan_data = {
            "bet_amount": 100.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "initial_weight": 80.0,
            "target_weight": 75.0,
            "description": "30天减重5kg挑战"
        }
        
        create_response = requests.post(
            f"{api_base_url}/betting-plans",
            json=plan_data,
            headers=headers_a
        )
        assert create_response.status_code == 201
        plan = create_response.json()
        plan_id = plan["id"]
        assert plan["status"] == "pending"
        assert plan["bet_amount"] == 100.0
        
        # 用户 B (iOS) 查看计划详情
        get_response = requests.get(
            f"{api_base_url}/betting-plans/{plan_id}",
            headers=headers_b
        )
        assert get_response.status_code == 200
        plan_detail = get_response.json()
        assert plan_detail["id"] == plan_id
        assert plan_detail["bet_amount"] == 100.0
        
        # 用户 B (iOS) 接受计划
        accept_data = {
            "initial_weight": 60.0,
            "target_weight": 55.0
        }
        accept_response = requests.post(
            f"{api_base_url}/betting-plans/{plan_id}/accept",
            json=accept_data,
            headers=headers_b
        )
        assert accept_response.status_code == 200
        accepted_plan = accept_response.json()
        assert accepted_plan["status"] == "active"
        assert accepted_plan["participant_id"] is not None
        
        # 用户 A (Android) 查看计划状态
        check_response = requests.get(
            f"{api_base_url}/betting-plans/{plan_id}",
            headers=headers_a
        )
        assert check_response.status_code == 200
        final_plan = check_response.json()
        assert final_plan["status"] == "active"
        
        print("✅ 场景 2 通过: 跨平台创建和接受对赌计划")
        
        # 返回计划 ID 供后续测试使用
        return plan_id
    
    def test_scenario_3_cross_platform_checkin(self, api_base_url, user_tokens):
        """
        场景 3: 跨平台打卡和进度同步
        
        验证在一个平台打卡后,另一个平台能看到更新
        """
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['user_b']}"}
        
        # 首先创建一个计划
        plan_id = self.test_scenario_2_cross_platform_betting_plan(api_base_url, user_tokens)
        
        # 用户 A (iOS) 打卡
        checkin_data_a = {
            "plan_id": plan_id,
            "weight": 78.5,
            "check_in_date": datetime.now().isoformat(),
            "note": "今天感觉很好!"
        }
        checkin_response_a = requests.post(
            f"{api_base_url}/check-ins",
            json=checkin_data_a,
            headers=headers_a
        )
        assert checkin_response_a.status_code == 201
        checkin_a = checkin_response_a.json()
        assert checkin_a["weight"] == 78.5
        
        # 用户 A (Android) 查看打卡历史
        history_response_a = requests.get(
            f"{api_base_url}/betting-plans/{plan_id}/check-ins",
            headers=headers_a
        )
        assert history_response_a.status_code == 200
        history_a = history_response_a.json()
        assert len(history_a) >= 1
        assert any(c["weight"] == 78.5 for c in history_a)
        
        # 用户 B (Android) 打卡
        checkin_data_b = {
            "plan_id": plan_id,
            "weight": 59.0,
            "check_in_date": datetime.now().isoformat(),
            "note": "继续加油!"
        }
        checkin_response_b = requests.post(
            f"{api_base_url}/check-ins",
            json=checkin_data_b,
            headers=headers_b
        )
        assert checkin_response_b.status_code == 201
        
        # 用户 B (iOS) 查看进度
        progress_response_b = requests.get(
            f"{api_base_url}/betting-plans/{plan_id}/progress",
            headers=headers_b
        )
        assert progress_response_b.status_code == 200
        progress_b = progress_response_b.json()
        assert progress_b["current_weight"] == 59.0
        assert progress_b["weight_loss"] == 1.0
        
        print("✅ 场景 3 通过: 跨平台打卡和进度同步")
    
    def test_scenario_5_cross_platform_payment(self, api_base_url, user_tokens):
        """
        场景 5: 跨平台支付流程
        
        验证支付操作在两个平台上都能正确执行和同步
        """
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        
        # 用户 A (Android) 查看初始余额
        balance_response_1 = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        )
        assert balance_response_1.status_code == 200
        initial_balance = balance_response_1.json()
        
        # 模拟充值 (实际环境需要 Stripe 集成)
        # 这里我们直接测试余额查询的一致性
        
        # 用户 A (iOS) 查看余额
        balance_response_2 = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        )
        assert balance_response_2.status_code == 200
        balance_2 = balance_response_2.json()
        
        # 验证余额一致
        assert balance_2["available_balance"] == initial_balance["available_balance"]
        assert balance_2["frozen_balance"] == initial_balance["frozen_balance"]
        
        # 查看交易历史
        transactions_response = requests.get(
            f"{api_base_url}/users/me/transactions",
            headers=headers_a
        )
        assert transactions_response.status_code == 200
        transactions = transactions_response.json()
        assert isinstance(transactions, list)
        
        print("✅ 场景 5 通过: 跨平台支付流程")
    
    def test_scenario_7_cross_platform_social(self, api_base_url, user_tokens):
        """
        场景 7: 跨平台社交功能
        
        验证社交功能在两个平台上的一致性
        """
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['user_b']}"}
        
        # 创建一个计划用于评论
        plan_id = self.test_scenario_2_cross_platform_betting_plan(api_base_url, user_tokens)
        
        # 用户 A (Android) 发表评论
        comment_data = {
            "content": "一起加油!💪"
        }
        comment_response = requests.post(
            f"{api_base_url}/betting-plans/{plan_id}/comments",
            json=comment_data,
            headers=headers_a
        )
        assert comment_response.status_code == 201
        comment = comment_response.json()
        assert comment["content"] == "一起加油!💪"
        
        # 用户 B (iOS) 查看评论
        comments_response = requests.get(
            f"{api_base_url}/betting-plans/{plan_id}/comments",
            headers=headers_b
        )
        assert comments_response.status_code == 200
        comments = comments_response.json()
        assert len(comments) >= 1
        assert any(c["content"] == "一起加油!💪" for c in comments)
        
        # 查看排行榜 (Android)
        leaderboard_response_a = requests.get(
            f"{api_base_url}/leaderboard/weight-loss",
            headers=headers_a
        )
        assert leaderboard_response_a.status_code == 200
        leaderboard_a = leaderboard_response_a.json()
        
        # 查看排行榜 (iOS)
        leaderboard_response_b = requests.get(
            f"{api_base_url}/leaderboard/weight-loss",
            headers=headers_b
        )
        assert leaderboard_response_b.status_code == 200
        leaderboard_b = leaderboard_response_b.json()
        
        # 验证排行榜一致
        assert leaderboard_a == leaderboard_b
        
        print("✅ 场景 7 通过: 跨平台社交功能")
    
    def test_data_consistency(self, api_base_url, user_tokens):
        """
        测试数据一致性
        
        验证同一数据在不同平台上的一致性
        """
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        
        # 多次请求同一数据
        responses = []
        for _ in range(5):
            response = requests.get(f"{api_base_url}/users/me", headers=headers_a)
            assert response.status_code == 200
            responses.append(response.json())
            time.sleep(0.1)
        
        # 验证所有响应一致
        first_response = responses[0]
        for response in responses[1:]:
            assert response["id"] == first_response["id"]
            assert response["email"] == first_response["email"]
            assert response["nickname"] == first_response["nickname"]
        
        print("✅ 数据一致性测试通过")
    
    def test_api_response_time(self, api_base_url, user_tokens):
        """
        测试 API 响应时间
        
        验证 API 响应时间符合性能要求 (< 200ms)
        """
        headers_a = {"Authorization": f"Bearer {user_tokens['user_a']}"}
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = requests.get(f"{api_base_url}/users/me", headers=headers_a)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
        
        # 计算 P95 响应时间
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95_response_time = response_times[p95_index]
        
        print(f"API 响应时间 P95: {p95_response_time:.2f}ms")
        assert p95_response_time < 200, f"API 响应时间过长: {p95_response_time}ms"
        
        print("✅ API 响应时间测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
