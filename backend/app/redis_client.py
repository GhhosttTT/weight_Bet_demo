"""
Redis 客户端管理
"""
import redis
from app.config import settings
from typing import Optional
import time
import fnmatch


class FakeRedis:
    """
    假的 Redis 客户端，用于在没有 Redis 时提供兼容接口
    """
    def __init__(self):
        self._data = {}
        self._sorted_sets = {}
        self._expires = {}

    def _purge_if_expired(self, key):
        if key in self._expires and self._expires[key] <= time.time():
            self._sorted_sets.pop(key, None)
            self._data.pop(key, None)
            self._expires.pop(key, None)
    
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
            self._sorted_sets.pop(key, None)
            self._expires.pop(key, None)
        return len(keys)

    def scan_iter(self, match=None):
        """提供测试环境所需的 Redis scan_iter 兼容接口。"""
        keys = set(self._data) | set(self._sorted_sets)
        for key in keys:
            if match is None or fnmatch.fnmatch(key, match):
                yield key
    
    def exists(self, key):
        return 1 if key in self._data else 0
    
    def setex(self, key, time, value):
        self._data[key] = value
        return True

    def zremrangebyscore(self, key, min_score, max_score):
        self._purge_if_expired(key)
        entries = self._sorted_sets.setdefault(key, {})
        removed = [member for member, score in entries.items()
                   if min_score <= score <= max_score]
        for member in removed:
            del entries[member]
        return len(removed)

    def zcard(self, key):
        self._purge_if_expired(key)
        return len(self._sorted_sets.get(key, {}))

    def zadd(self, key, mapping):
        self._purge_if_expired(key)
        self._sorted_sets.setdefault(key, {}).update(mapping)
        return len(mapping)

    def expire(self, key, seconds):
        self._expires[key] = time.time() + seconds
        return True


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
        results = []
        for command in self.commands:
            name, *args = command
            results.append(getattr(self.client, name)(*args))
        return results


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
except Exception as error:
    # 生产/预发布环境不能静默降级到进程内 Redis，否则多 worker 下限流和缓存
    # 会各自维护一份状态，造成安全策略失效或数据不一致。
    if settings.ENVIRONMENT.strip().lower() in {"production", "prod", "staging"}:
        raise RuntimeError("生产环境 Redis 连接失败，拒绝使用进程内 FakeRedis") from error
    # 开发和测试环境保留无外部 Redis 时的兼容行为。
    redis_client = FakeRedis()


def get_redis():
    """
    获取 Redis 客户端
    用于依赖注入
    """
    return redis_client
