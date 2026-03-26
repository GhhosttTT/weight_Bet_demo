"""
缓存服务 - 实现 Redis 缓存策略
"""
import json
from typing import Optional, Any
from app.redis_client import get_redis
from app.logger import get_logger

logger = get_logger()


class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        self.redis = get_redis()
        
        # 缓存 TTL 配置 (秒)
        self.TTL_USER_INFO = 600  # 10分钟
        self.TTL_PLAN_DETAILS = 300  # 5分钟
        self.TTL_LEADERBOARD = 300  # 5分钟
        self.TTL_USER_BALANCE = 60  # 1分钟
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """生成缓存键"""
        return f"{prefix}:{identifier}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Redis get error: {}", e)
            return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """设置缓存数据"""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error("Redis set error: {}", e)
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error("Redis delete error: {}", e)
            return False
    
    def delete_pattern(self, pattern: str) -> bool:
        """删除匹配模式的所有键"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error("Redis delete pattern error: {}", e)
            return False
    
    # 用户信息缓存
    def get_user_info(self, user_id: str) -> Optional[dict]:
        """获取用户信息缓存"""
        key = self._make_key("user", user_id)
        return self.get(key)
    
    def set_user_info(self, user_id: str, user_data: dict) -> bool:
        """设置用户信息缓存"""
        key = self._make_key("user", user_id)
        return self.set(key, user_data, self.TTL_USER_INFO)
    
    def invalidate_user_info(self, user_id: str) -> bool:
        """使用户信息缓存失效"""
        key = self._make_key("user", user_id)
        return self.delete(key)
    
    # 计划详情缓存
    def get_plan_details(self, plan_id: str) -> Optional[dict]:
        """获取计划详情缓存"""
        key = self._make_key("plan", plan_id)
        return self.get(key)
    
    def set_plan_details(self, plan_id: str, plan_data: dict) -> bool:
        """设置计划详情缓存"""
        key = self._make_key("plan", plan_id)
        return self.set(key, plan_data, self.TTL_PLAN_DETAILS)
    
    def invalidate_plan_details(self, plan_id: str) -> bool:
        """使计划详情缓存失效"""
        key = self._make_key("plan", plan_id)
        return self.delete(key)
    
    # 排行榜缓存
    def get_leaderboard(self, leaderboard_type: str) -> Optional[list]:
        """获取排行榜缓存"""
        key = self._make_key("leaderboard", leaderboard_type)
        return self.get(key)
    
    def set_leaderboard(self, leaderboard_type: str, data: list) -> bool:
        """设置排行榜缓存"""
        key = self._make_key("leaderboard", leaderboard_type)
        return self.set(key, data, self.TTL_LEADERBOARD)
    
    def invalidate_all_leaderboards(self) -> bool:
        """使所有排行榜缓存失效"""
        return self.delete_pattern("leaderboard:*")
    
    # 用户余额缓存
    def get_user_balance(self, user_id: str) -> Optional[dict]:
        """获取用户余额缓存"""
        key = self._make_key("balance", user_id)
        return self.get(key)
    
    def set_user_balance(self, user_id: str, balance_data: dict) -> bool:
        """设置用户余额缓存"""
        key = self._make_key("balance", user_id)
        return self.set(key, balance_data, self.TTL_USER_BALANCE)
    
    def invalidate_user_balance(self, user_id: str) -> bool:
        """使用户余额缓存失效"""
        key = self._make_key("balance", user_id)
        return self.delete(key)


# 创建全局缓存服务实例
cache_service = CacheService()
