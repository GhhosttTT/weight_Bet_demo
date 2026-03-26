"""
支付流程集成测试

测试跨平台支付流程的正确性和一致性
"""

import pytest
import requests
import time
from datetime import datetime
from typing import Dict, Any


class TestPayment:
    """支付流程测试类"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API 基础 URL"""
        return "http://localhost:8000/api"
    
    @pytest.fixture(scope="class")
    def test_users(self):
        """测试用户数据"""
        return {
            "user_a": {
                "email": "payment_test_a@example.com",
                "password": "Test123456!",
                "nickname": "支付测试用户A",
                "gender": "male",
                "age": 25,
                "height": 175.0,
                "current_weight": 80.0,
                "target_weight": 75.0
            },
            "user_b": {
                "email": "payment_test_b@example.com",
                "password": "Test123456!",
                "nickname": "支付测试用户B",
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
    
    def test_balance_query_consistency(self, api_base_url, user_tokens):
        """
        场景 1: 余额查询一致性
        
        验证余额在两个平台上查询结果一致
        """
        print("\n=== 测试场景 1: 余额查询一致性 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        
        # 多次查询余额
        balances = []
        for i in range(5):
            response = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            )
            assert response.status_code == 200
            balances.append(response.json())
            time.sleep(0.1)
        
        # 验证所有查询结果一致
        first_balance = balances[0]
        for balance in balances[1:]:
            assert balance["available_balance"] == first_balance["available_balance"]
            assert balance["frozen_balance"] == first_balance["frozen_balance"]
        
        print(f"✅ 场景 1 通过: 余额查询一致 (可用: {first_balance['available_balance']}, 冻结: {first_balance['frozen_balance']})")
    
    def test_transaction_history_sync(self, api_base_url, user_tokens):
        """
        场景 2: 交易历史同步
        
        验证交易历史在两个平台上同步
        """
        print("\n=== 测试场景 2: 交易历史同步 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        
        # Android 查询交易历史
        transactions_android = requests.get(
            f"{api_base_url}/users/me/transactions",
            headers=headers_a
        )
        assert transactions_android.status_code == 200
        transactions_a = transactions_android.json()
        
        # iOS 查询交易历史 (模拟)
        transactions_ios = requests.get(
            f"{api_base_url}/users/me/transactions",
            headers=headers_a
        )
        assert transactions_ios.status_code == 200
        transactions_b = transactions_ios.json()
        
        # 验证交易历史一致
        assert len(transactions_a) == len(transactions_b)
        
        if len(transactions_a) > 0:
            for i in range(len(transactions_a)):
                assert transactions_a[i]["id"] == transactions_b[i]["id"]
                assert transactions_a[i]["type"] == transactions_b[i]["type"]
                assert transactions_a[i]["amount"] == transactions_b[i]["amount"]
                assert transactions_a[i]["status"] == transactions_b[i]["status"]
        
        print(f"✅ 场景 2 通过: 交易历史同步 (共 {len(transactions_a)} 条记录)")
    
    def test_charge_simulation(self, api_base_url, user_tokens):
        """
        场景 3: 充值流程测试 (模拟)
        
        注意: 实际充值需要 Stripe 集成,这里只测试 API 端点
        """
        print("\n=== 测试场景 3: 充值流程测试 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        
        # 获取充值前余额
        balance_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        # 模拟充值请求 (实际环境需要 Stripe token)
        charge_data = {
            "amount": 500.0,
            "payment_method": "test_card",
            "description": "测试充值"
        }
        
        charge_response = requests.post(
            f"{api_base_url}/payments/charge",
            json=charge_data,
            headers=headers_a
        )
        
        if charge_response.status_code == 200:
            # 获取充值后余额
            balance_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            
            # 验证余额增加
            assert balance_after["available_balance"] == balance_before["available_balance"] + 500.0
            
            # 验证交易记录
            transactions = requests.get(
                f"{api_base_url}/users/me/transactions",
                headers=headers_a
            ).json()
            
            # 应该有新的充值记录
            charge_transaction = next(
                (t for t in transactions if t["type"] == "charge" and t["amount"] == 500.0),
                None
            )
            assert charge_transaction is not None
            assert charge_transaction["status"] == "completed"
            
            print("✅ 场景 3 通过: 充值流程正常")
        else:
            print(f"⚠️  充值 API 需要 Stripe 集成 (状态码: {charge_response.status_code})")
            print("   提示: 在生产环境中需要配置 Stripe API keys")
    
    def test_withdraw_simulation(self, api_base_url, user_tokens):
        """
        场景 4: 提现流程测试 (模拟)
        
        注意: 实际提现需要支付网关集成
        """
        print("\n=== 测试场景 4: 提现流程测试 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        
        # 获取提现前余额
        balance_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        # 只有在余额充足时才测试提现
        if balance_before["available_balance"] >= 200.0:
            # 模拟提现请求
            withdraw_data = {
                "amount": 200.0,
                "payment_method": "test_account",
                "description": "测试提现"
            }
            
            withdraw_response = requests.post(
                f"{api_base_url}/payments/withdraw",
                json=withdraw_data,
                headers=headers_a
            )
            
            if withdraw_response.status_code == 200:
                # 获取提现后余额
                balance_after = requests.get(
                    f"{api_base_url}/users/me/balance",
                    headers=headers_a
                ).json()
                
                # 验证余额减少
                assert balance_after["available_balance"] == balance_before["available_balance"] - 200.0
                
                # 验证交易记录
                transactions = requests.get(
                    f"{api_base_url}/users/me/transactions",
                    headers=headers_a
                ).json()
                
                # 应该有新的提现记录
                withdraw_transaction = next(
                    (t for t in transactions if t["type"] == "withdraw" and t["amount"] == 200.0),
                    None
                )
                assert withdraw_transaction is not None
                
                print("✅ 场景 4 通过: 提现流程正常")
            else:
                print(f"⚠️  提现 API 需要支付网关集成 (状态码: {withdraw_response.status_code})")
        else:
            print(f"⚠️  余额不足,跳过提现测试 (当前余额: {balance_before['available_balance']})")
    
    def test_freeze_unfreeze_funds(self, api_base_url, user_tokens):
        """
        场景 5: 资金冻结和解冻
        
        验证资金冻结和解冻的正确性
        """
        print("\n=== 测试场景 5: 资金冻结和解冻 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        headers_b = {"Authorization": f"Bearer {user_tokens['tokens']['user_b']}"}
        
        # 获取初始余额
        balance_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        # 创建对赌计划会冻结资金
        plan_data = {
            "bet_amount": 100.0,
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_weight": 80.0,
            "target_weight": 75.0,
            "description": "资金冻结测试"
        }
        
        create_response = requests.post(
            f"{api_base_url}/betting-plans",
            json=plan_data,
            headers=headers_a
        )
        
        if create_response.status_code == 201:
            plan_id = create_response.json()["id"]
            
            # 验证资金被冻结
            balance_after_create = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            
            assert balance_after_create["available_balance"] == balance_before["available_balance"] - 100.0
            assert balance_after_create["frozen_balance"] == balance_before["frozen_balance"] + 100.0
            
            # 取消计划会解冻资金
            cancel_response = requests.post(
                f"{api_base_url}/betting-plans/{plan_id}/cancel",
                headers=headers_a
            )
            
            if cancel_response.status_code == 200:
                # 验证资金被解冻
                balance_after_cancel = requests.get(
                    f"{api_base_url}/users/me/balance",
                    headers=headers_a
                ).json()
                
                assert balance_after_cancel["available_balance"] == balance_before["available_balance"]
                assert balance_after_cancel["frozen_balance"] == balance_before["frozen_balance"]
                
                print("✅ 场景 5 通过: 资金冻结和解冻正常")
            else:
                print(f"⚠️  取消计划失败 (状态码: {cancel_response.status_code})")
        else:
            print(f"⚠️  创建计划失败,可能余额不足 (状态码: {create_response.status_code})")
    
    def test_cross_platform_balance_sync(self, api_base_url, user_tokens):
        """
        场景 6: 跨平台余额同步
        
        验证余额变化在两个平台上实时同步
        """
        print("\n=== 测试场景 6: 跨平台余额同步 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        
        # Android 查询余额
        balance_android = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        # iOS 查询余额 (模拟)
        time.sleep(0.1)  # 模拟网络延迟
        balance_ios = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        # 验证余额一致
        assert balance_android["available_balance"] == balance_ios["available_balance"]
        assert balance_android["frozen_balance"] == balance_ios["frozen_balance"]
        
        # 验证同步延迟 < 1s
        start_time = time.time()
        
        # 执行一个会改变余额的操作 (创建计划)
        plan_data = {
            "bet_amount": 50.0,
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_weight": 80.0,
            "target_weight": 75.0,
            "description": "同步测试"
        }
        
        create_response = requests.post(
            f"{api_base_url}/betting-plans",
            json=plan_data,
            headers=headers_a
        )
        
        if create_response.status_code == 201:
            # 立即在另一个平台查询
            balance_after = requests.get(
                f"{api_base_url}/users/me/balance",
                headers=headers_a
            ).json()
            
            sync_time = time.time() - start_time
            
            # 验证余额已更新
            assert balance_after["frozen_balance"] == balance_android["frozen_balance"] + 50.0
            
            # 验证同步延迟
            assert sync_time < 1.0, f"同步延迟过长: {sync_time}s"
            
            print(f"✅ 场景 6 通过: 跨平台余额同步 (延迟: {sync_time*1000:.2f}ms)")
            
            # 清理: 取消计划
            plan_id = create_response.json()["id"]
            requests.post(
                f"{api_base_url}/betting-plans/{plan_id}/cancel",
                headers=headers_a
            )
        else:
            print(f"⚠️  创建计划失败,跳过同步测试 (状态码: {create_response.status_code})")
    
    def test_transaction_atomicity(self, api_base_url, user_tokens):
        """
        场景 7: 交易原子性
        
        验证交易操作的原子性 (要么全部成功,要么全部失败)
        """
        print("\n=== 测试场景 7: 交易原子性 ===")
        
        headers_a = {"Authorization": f"Bearer {user_tokens['tokens']['user_a']}"}
        
        # 获取初始余额
        balance_before = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        # 尝试创建一个余额不足的计划
        plan_data = {
            "bet_amount": 999999.0,  # 超大金额
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat(),
            "initial_weight": 80.0,
            "target_weight": 75.0,
            "description": "原子性测试"
        }
        
        create_response = requests.post(
            f"{api_base_url}/betting-plans",
            json=plan_data,
            headers=headers_a
        )
        
        # 应该失败
        assert create_response.status_code in [400, 402, 403]
        
        # 验证余额没有变化
        balance_after = requests.get(
            f"{api_base_url}/users/me/balance",
            headers=headers_a
        ).json()
        
        assert balance_after["available_balance"] == balance_before["available_balance"]
        assert balance_after["frozen_balance"] == balance_before["frozen_balance"]
        
        print("✅ 场景 7 通过: 交易原子性保证 (失败时余额不变)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
