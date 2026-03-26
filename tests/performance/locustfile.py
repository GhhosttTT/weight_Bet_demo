"""
性能测试脚本 - 使用 Locust 进行负载测试

安装依赖:
pip install locust

运行测试:
locust -f tests/performance/locustfile.py --host=http://localhost:8000

访问 Web UI: http://localhost:8089
"""

from locust import HttpUser, task, between
import random
import json

class WeightLossBettingUser(HttpUser):
    """模拟减肥对赌 APP 用户行为"""
    
    wait_time = between(1, 3)  # 用户操作间隔 1-3 秒
    
    def on_start(self):
        """用户开始时执行 - 注册并登录"""
        # 注册新用户
        email = f"test_user_{random.randint(1000, 9999)}@example.com"
        password = "Test123456"
        
        register_response = self.client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "nickname": f"TestUser{random.randint(1000, 9999)}",
            "gender": random.choice(["male", "female"]),
            "age": random.randint(20, 50),
            "height": random.uniform(150, 190),
            "current_weight": random.uniform(60, 100),
            "target_weight": random.uniform(50, 80)
        })
        
        if register_response.status_code == 201:
            data = register_response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
        else:
            # 如果注册失败,尝试登录
            login_response = self.client.post("/api/auth/login", json={
                "email": email,
                "password": password
            })
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
    
    def get_headers(self):
        """获取带认证的请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def view_user_profile(self):
        """查看用户信息 - 高频操作"""
        self.client.get(
            f"/api/users/{self.user_id}",
            headers=self.get_headers(),
            name="/api/users/[userId]"
        )
    
    @task(2)
    def view_betting_plans(self):
        """查看对赌计划列表 - 中频操作"""
        self.client.get(
            f"/api/users/{self.user_id}/betting-plans",
            headers=self.get_headers(),
            name="/api/users/[userId]/betting-plans"
        )
    
    @task(1)
    def create_betting_plan(self):
        """创建对赌计划 - 低频操作"""
        self.client.post(
            "/api/betting-plans",
            headers=self.get_headers(),
            json={
                "bet_amount": random.uniform(50, 500),
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "initial_weight": random.uniform(70, 90),
                "target_weight": random.uniform(60, 80),
                "description": "30天减重挑战"
            },
            name="/api/betting-plans"
        )
    
    @task(2)
    def check_in(self):
        """打卡 - 中频操作"""
        # 假设有一个活跃的计划 ID
        plan_id = "test-plan-id"
        self.client.post(
            "/api/check-ins",
            headers=self.get_headers(),
            json={
                "plan_id": plan_id,
                "weight": random.uniform(60, 90),
                "check_in_date": "2024-01-15T10:00:00Z",
                "note": "今天感觉不错"
            },
            name="/api/check-ins"
        )
    
    @task(1)
    def view_leaderboard(self):
        """查看排行榜 - 低频操作"""
        leaderboard_type = random.choice(["weight-loss", "check-in-streak", "win-rate"])
        self.client.get(
            f"/api/leaderboard/{leaderboard_type}",
            headers=self.get_headers(),
            name="/api/leaderboard/[type]"
        )
    
    @task(1)
    def view_balance(self):
        """查看账户余额 - 低频操作"""
        self.client.get(
            f"/api/users/{self.user_id}/balance",
            headers=self.get_headers(),
            name="/api/users/[userId]/balance"
        )


class AdminUser(HttpUser):
    """模拟管理员用户行为"""
    
    wait_time = between(5, 10)
    
    def on_start(self):
        """管理员登录"""
        login_response = self.client.post("/api/auth/login", json={
            "email": "admin@example.com",
            "password": "AdminPassword123"
        })
        if login_response.status_code == 200:
            data = login_response.json()
            self.token = data.get("access_token")
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task
    def view_all_plans(self):
        """查看所有计划"""
        self.client.get(
            "/api/admin/betting-plans",
            headers=self.get_headers(),
            name="/api/admin/betting-plans"
        )
    
    @task
    def view_settlements(self):
        """查看结算记录"""
        self.client.get(
            "/api/admin/settlements",
            headers=self.get_headers(),
            name="/api/admin/settlements"
        )
