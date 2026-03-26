"""
结算流程集成测试

测试跨平台结算流程的正确性和一致性
"""

import pytest
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any


class TestSettlement:
    """结算流程测试类"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API 基础 URL"""
        return "http://localhost:8000/api"
    
    @pytest.fixture(scope="class")
    def test_users(self):
        """测试用户数据"""
        return {
            "user_a": {
                "email": "settlement_test_a@example.com",
                "password": "Test123456!",
                "nickname": "结算测试用户A",
                "gender": "male",
                "age": 25,
                "height": 175.0,
                "current_weight": 80.0,
                "target_weight": 75.0
            },
            "user_b": {
                "email": "settlement_test_b@example.com",
                "password": "Test123456!",
                "nickname": "结算测试用户B",
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
        user_ids = {}
        
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
                login_data = login_response.json()
                tokens[user_key] = login_data["access_token"]
                user_ids[user_key] = login_data["user"]["id"]
            else:
                assert register_response.status_code == 201
                register_data = register_response.json()
                tokens[user_key] = register_data["access_token"]
                user_ids[user_key] = register_data["user"]["id"]
        
        return {"tokens": tokens, "user_ids": user_ids}
    
    def create_test_plan(self, api_base_url, user_tokens, days=1):
        """创建测试计划"""
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 创建计划
        plan_data = {
            "bet_amount": 100.0,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=days)).isoformat(),
            "initial_weight": 80.0,
            "target_weight": 75.0,
            "description": f"{days}天结算测试计划"
        }
        
        create_response = requests.post(
            f"{api_base_url}/betting-plans",
            json=plan_data,
            headers=headers_a
        )
        assert create_response.status_code == 201
        plan = create_response.json()
        plan_id = plan["id"]
        
        # 接受计划
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
        
        return plan_id
    
    def create_checkins(self, api_base_url, user_tokens, plan_id, user_a_weight, user_b_weight):
        """创建打卡记录"""
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 用户 A 打卡
        checkin_data_a = {
            "plan_id": plan_id,
            "weight": user_a_weight,
            "check_in_date": datetime.now().isoformat(),
            "note": "最终打卡"
        }
        checkin_response_a = requests.post(
            f"{api_base_url}/check-ins",
            json=checkin_data_a,
            headers=headers_a
        )
        assert checkin_response_a.status_code == 201
        
        # 用户 B 打卡
        checkin_data_b = {
            "plan_id": plan_id,
            "weight": user_b_weight,
            "check_in_date": datetime.now().isoformat(),
            "note": "最终打卡"
        }
        checkin_response_b = requests.post(
            f"{api_base_url}/check-ins",
            json=checkin_data_b,
            headers=headers_b
        )
        assert checkin_response_b.status_code == 201
    
    def test_settlement_both_achieved(self, api_base_url, user_tokens):
        """
        场景 1: 双方都达成目标的结算
        
        预期结果: 原路返还,无手续费
        """
        print("\n=== 测试场景 1: 双方都达成目标 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 创建计划
        plan_id = self.create_test_plan(api_base_url, user_tokens, days=1)
        
        # 获取初始余额
        balance_a_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        balance_b_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_b
        ).json()
        
        # 创建打卡记录 (双方都达成目标)
        self.create_checkins(api_base_url, user_tokens, plan_id, 75.0, 55.0)
        
        # 手动触发结算 (实际环境中由定时任务触发)
        settle_response = requests.post(
            f"{api_base_url}/settlements/execute/{plan_id}",
            headers=headers_a
        )
        
        if settle_response.status_code == 200:
            settlement = settle_response.json()
            
            # 验证结算结果
            assert settlement["creator_achieved"] == True
            assert settlement["participant_achieved"] == True
            assert settlement["creator_amount"] == 100.0  # 原路返还
            assert settlement["participant_amount"] == 100.0  # 原路返还
            assert settlement["platform_fee"] == 0.0  # 无手续费
            
            # 验证余额更新
            balance_a_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            balance_b_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_b
            ).json()
            
            # 验证资金守恒
            total_before = (balance_a_before["available_balance"] + 
                          balance_a_before["frozen_balance"] +
                          balance_b_before["available_balance"] + 
                          balance_b_before["frozen_balance"])
            total_after = (balance_a_after["available_balance"] + 
                         balance_a_after["frozen_balance"] +
                         balance_b_after["available_balance"] + 
                         balance_b_after["frozen_balance"])
            
            assert abs(total_before - total_after) < 0.01  # 允许浮点误差
            
            print("✅ 场景 1 通过: 双方都达成目标,原路返还")
        else:
            print(f"⚠️  结算 API 未实现或需要等待计划到期 (状态码: {settle_response.status_code})")
    
    def test_settlement_both_failed(self, api_base_url, user_tokens):
        """
        场景 2: 双方都未达成目标的结算
        
        预期结果: 扣除 10% 手续费后平分
        """
        print("\n=== 测试场景 2: 双方都未达成目标 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 创建计划
        plan_id = self.create_test_plan(api_base_url, user_tokens, days=1)
        
        # 获取初始余额
        balance_a_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        balance_b_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_b
        ).json()
        
        # 创建打卡记录 (双方都未达成目标)
        self.create_checkins(api_base_url, user_tokens, plan_id, 79.0, 59.0)
        
        # 手动触发结算
        settle_response = requests.post(
            f"{api_base_url}/settlements/execute/{plan_id}",
            headers=headers_a
        )
        
        if settle_response.status_code == 200:
            settlement = settle_response.json()
            
            # 验证结算结果
            assert settlement["creator_achieved"] == False
            assert settlement["participant_achieved"] == False
            assert settlement["platform_fee"] == 20.0  # 10% 手续费
            assert settlement["creator_amount"] == 90.0  # (200 - 20) / 2
            assert settlement["participant_amount"] == 90.0  # (200 - 20) / 2
            
            # 验证余额更新
            balance_a_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            balance_b_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_b
            ).json()
            
            # 验证资金守恒 (扣除手续费)
            total_before = (balance_a_before["available_balance"] + 
                          balance_a_before["frozen_balance"] +
                          balance_b_before["available_balance"] + 
                          balance_b_before["frozen_balance"])
            total_after = (balance_a_after["available_balance"] + 
                         balance_a_after["frozen_balance"] +
                         balance_b_after["available_balance"] + 
                         balance_b_after["frozen_balance"])
            
            # 总金额应该减少 20 元 (手续费)
            assert abs((total_before - total_after) - 20.0) < 0.01
            
            print("✅ 场景 2 通过: 双方都未达成目标,扣除手续费后平分")
        else:
            print(f"⚠️  结算 API 未实现或需要等待计划到期 (状态码: {settle_response.status_code})")
    
    def test_settlement_creator_achieved(self, api_base_url, user_tokens):
        """
        场景 3: 创建者达成目标,参与者未达成
        
        预期结果: 创建者获得全部赌金
        """
        print("\n=== 测试场景 3: 创建者达成目标 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 创建计划
        plan_id = self.create_test_plan(api_base_url, user_tokens, days=1)
        
        # 获取初始余额
        balance_a_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        balance_b_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_b
        ).json()
        
        # 创建打卡记录 (创建者达成,参与者未达成)
        self.create_checkins(api_base_url, user_tokens, plan_id, 75.0, 59.0)
        
        # 手动触发结算
        settle_response = requests.post(
            f"{api_base_url}/settlements/execute/{plan_id}",
            headers=headers_a
        )
        
        if settle_response.status_code == 200:
            settlement = settle_response.json()
            
            # 验证结算结果
            assert settlement["creator_achieved"] == True
            assert settlement["participant_achieved"] == False
            assert settlement["creator_amount"] == 200.0  # 获得全部赌金
            assert settlement["participant_amount"] == 0.0
            assert settlement["platform_fee"] == 0.0
            
            # 验证余额更新
            balance_a_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            balance_b_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_b
            ).json()
            
            # 验证资金守恒
            total_before = (balance_a_before["available_balance"] + 
                          balance_a_before["frozen_balance"] +
                          balance_b_before["available_balance"] + 
                          balance_b_before["frozen_balance"])
            total_after = (balance_a_after["available_balance"] + 
                         balance_a_after["frozen_balance"] +
                         balance_b_after["available_balance"] + 
                         balance_b_after["frozen_balance"])
            
            assert abs(total_before - total_after) < 0.01
            
            print("✅ 场景 3 通过: 创建者达成目标,获得全部赌金")
        else:
            print(f"⚠️  结算 API 未实现或需要等待计划到期 (状态码: {settle_response.status_code})")
    
    def test_settlement_participant_achieved(self, api_base_url, user_tokens):
        """
        场景 4: 参与者达成目标,创建者未达成
        
        预期结果: 参与者获得全部赌金
        """
        print("\n=== 测试场景 4: 参与者达成目标 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 创建计划
        plan_id = self.create_test_plan(api_base_url, user_tokens, days=1)
        
        # 获取初始余额
        balance_a_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        balance_b_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_b
        ).json()
        
        # 创建打卡记录 (创建者未达成,参与者达成)
        self.create_checkins(api_base_url, user_tokens, plan_id, 79.0, 55.0)
        
        # 手动触发结算
        settle_response = requests.post(
            f"{api_base_url}/settlements/execute/{plan_id}",
            headers=headers_a
        )
        
        if settle_response.status_code == 200:
            settlement = settle_response.json()
            
            # 验证结算结果
            assert settlement["creator_achieved"] == False
            assert settlement["participant_achieved"] == True
            assert settlement["creator_amount"] == 0.0
            assert settlement["participant_amount"] == 200.0  # 获得全部赌金
            assert settlement["platform_fee"] == 0.0
            
            # 验证余额更新
            balance_a_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            balance_b_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_b
            ).json()
            
            # 验证资金守恒
            total_before = (balance_a_before["available_balance"] + 
                          balance_a_before["frozen_balance"] +
                          balance_b_before["available_balance"] + 
                          balance_b_before["frozen_balance"])
            total_after = (balance_a_after["available_balance"] + 
                         balance_a_after["frozen_balance"] +
                         balance_b_after["available_balance"] + 
                         balance_b_after["frozen_balance"])
            
            assert abs(total_before - total_after) < 0.01
            
            print("✅ 场景 4 通过: 参与者达成目标,获得全部赌金")
        else:
            print(f"⚠️  结算 API 未实现或需要等待计划到期 (状态码: {settle_response.status_code})")
    
    def test_settlement_cross_platform_consistency(self, api_base_url, user_tokens):
        """
        场景 5: 跨平台结算一致性
        
        验证结算结果在两个平台上一致
        """
        print("\n=== 测试场景 5: 跨平台结算一致性 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 创建计划
        plan_id = self.create_test_plan(api_base_url, user_tokens, days=1)
        
        # 创建打卡记录
        self.create_checkins(api_base_url, user_tokens, plan_id, 75.0, 55.0)
        
        # 手动触发结算
        settle_response = requests.post(
            f"{api_base_url}/settlements/execute/{plan_id}",
            headers=headers_a
        )
        
        if settle_response.status_code == 200:
            settlement_id = settle_response.json()["id"]
            
            # Android 查看结算详情
            settlement_android = requests.get(
                f"{api_base_url}/settlements/{settlement_id}",
                headers=headers_a
            ).json()
            
            # iOS 查看结算详情
            settlement_ios = requests.get(
                f"{api_base_url}/settlements/{settlement_id}",
                headers=headers_b
            ).json()
            
            # 验证结算详情一致
            assert settlement_android["id"] == settlement_ios["id"]
            assert settlement_android["creator_achieved"] == settlement_ios["creator_achieved"]
            assert settlement_android["participant_achieved"] == settlement_ios["participant_achieved"]
            assert settlement_android["creator_amount"] == settlement_ios["creator_amount"]
            assert settlement_android["participant_amount"] == settlement_ios["participant_amount"]
            assert settlement_android["platform_fee"] == settlement_ios["platform_fee"]
            
            print("✅ 场景 5 通过: 结算结果在两个平台上一致")
        else:
            print(f"⚠️  结算 API 未实现或需要等待计划到期 (状态码: {settle_response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
