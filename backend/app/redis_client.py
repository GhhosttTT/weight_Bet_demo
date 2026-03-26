"""
Redis 客户端管理
"""
import redis
from app.config import settings
from typing import Optional


class FakeRedis:
    """
    假的 Redis 客户端，用于在没有 Redis 时提供兼容接口
    """
    def __init__(self):
        self._data = {}
    
    def pipeline(self):
        return FakePipeline(self)
    
    def get(self, key):
        return self._data.get(key)
    
    def set(self, key, value, ex=None):
        self._data[key] = value
        return True
    
    def delete(self, *keys):
        for key in keys:
            self._data.pop(key, None)
        return len(keys)
    
    def exists(self, key):
        return 1 if key in self._data else 0


class FakePipeline:
    """
    假的 Redis Pipeline
    """
    def __init__(self, client):
        self.client = client
        self.commands = []
    
    def zremrangebyscore(self, key, min_score, max_score):
        self.commands.append(('zremrangebyscore', key, min_score, max_score))
        return self
    
    def zcard(self, key):
        self.commands.append(('zcard', key))
        return self
    
    def zadd(self, key, mapping):
        self.commands.append(('zadd', key, mapping))
        return self
    
    def expire(self, key, seconds):
        self.commands.append(('expire', key, seconds))
        return self
    
    def execute(self):
        # 返回假的结果
        return [None, 0, 1, True]


# 创建 Redis 客户端
redis_client: Optional[redis.Redis] = None

try:
    if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # 测试连接
        redis_client.ping()
except Exception:
    # 如果连接失败，使用假的 Redis 客户端
    redis_client = FakeRedis()


def get_redis():
    """
    获取 Redis 客户端
    用于依赖注入
    """
    return redis_client
