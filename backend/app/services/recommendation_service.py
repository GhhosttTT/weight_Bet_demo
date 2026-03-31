"""
推荐服务 - 调用模型侧获取个性化推荐
"""
import json
import httpx
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.user import User
from app.models.check_in import CheckIn
from app.schemas.recommendation import (
    UserProfileForRecommendation,
    CheckInRecordForRecommendation,
    RecommendationRequest,
    RecommendationResponse,
    ExerciseRecommendation,
    DietRecommendation
)
from app.config import settings
from app.redis_client import get_redis
from app.logger import get_logger

logger = get_logger()


class RecommendationService:
    """推荐服务类"""
    
    def __init__(self):
        self.redis = get_redis()
        self.model_url = settings.RECOMMENDATION_MODEL_URL
        self.cache_ttl = 3600  # 缓存1小时
    
    def _get_cache_key(self, user_id: str) -> str:
        """生成缓存键"""
        return f"recommendation:{user_id}"
    
    def _get_user_initial_weight(self, db: Session, user_id: str) -> Optional[float]:
        """获取用户的初始体重（最早的打卡记录）"""
        try:
            first_check_in = db.query(CheckIn)\
                .filter(CheckIn.user_id == user_id)\
                .order_by(CheckIn.check_in_date)\
                .first()
            return first_check_in.weight if first_check_in else None
        except Exception as e:
            logger.error("Error getting initial weight: {}", e)
            return None
    
    def _get_user_check_in_records(self, db: Session, user_id: str, limit: int = 30) -> List[CheckInRecordForRecommendation]:
        """获取用户最近的打卡记录"""
        try:
            check_ins = db.query(CheckIn)\
                .filter(CheckIn.user_id == user_id)\
                .order_by(desc(CheckIn.check_in_date))\
                .limit(limit)\
                .all()
            
            return [
                CheckInRecordForRecommendation(
                    check_in_date=check_in.check_in_date,
                    weight=check_in.weight,
                    note=check_in.note
                )
                for check_in in check_ins
            ]
        except Exception as e:
            logger.error("Error getting check-in records: {}", e)
            return []
    
    def _build_recommendation_request(
        self, 
        db: Session, 
        user_id: str, 
        request_type: str
    ) -> RecommendationRequest:
        """构建发送给模型侧的请求"""
        # 获取用户资料
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 获取初始体重
        initial_weight = self._get_user_initial_weight(db, user_id)
        
        # 构建用户资料
        user_profile = UserProfileForRecommendation(
            user_id=user_id,
            age=user.age,
            gender=user.gender.value if hasattr(user.gender, 'value') else str(user.gender),
            height=user.height,
            current_weight=user.current_weight,
            target_weight=user.target_weight,
            initial_weight=initial_weight
        )
        
        # 获取打卡记录
        check_in_records = self._get_user_check_in_records(db, user_id)
        
        return RecommendationRequest(
            user_profile=user_profile,
            check_in_records=check_in_records,
            request_type=request_type
        )
    
    async def _call_model_service(self, request: RecommendationRequest) -> RecommendationResponse:
        """调用模型侧获取推荐"""
        try:
            url = f"{self.model_url}/api/recommend"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=request.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return RecommendationResponse(**data)
                else:
                    logger.warning(
                        "Model service returned error: status={}, body={}",
                        response.status_code,
                        response.text
                    )
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="推荐服务暂时不可用"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Model service timeout")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="推荐服务响应超时"
            )
        except httpx.ConnectError:
            logger.error("Model service connection error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="无法连接到推荐服务"
            )
        except Exception as e:
            logger.error("Error calling model service: {}", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取推荐失败: {str(e)}"
            )
    
    def _get_cached_recommendation(self, user_id: str) -> Optional[RecommendationResponse]:
        """从缓存获取推荐"""
        try:
            key = self._get_cache_key(user_id)
            data = self.redis.get(key)
            if data:
                return RecommendationResponse(**json.loads(data))
            return None
        except Exception as e:
            logger.error("Error getting cached recommendation: {}", e)
            return None
    
    def _cache_recommendation(self, user_id: str, recommendation: RecommendationResponse):
        """缓存推荐结果"""
        try:
            key = self._get_cache_key(user_id)
            self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(recommendation.model_dump())
            )
        except Exception as e:
            logger.error("Error caching recommendation: {}", e)
    
    def _invalidate_cache(self, user_id: str):
        """使缓存失效"""
        try:
            key = self._get_cache_key(user_id)
            self.redis.delete(key)
        except Exception as e:
            logger.error("Error invalidating cache: {}", e)
    
    async def get_recommendation(
        self,
        db: Session,
        user_id: str,
        request_type: str = "login",
        use_cache: bool = True
    ) -> RecommendationResponse:
        """
        获取推荐
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            request_type: 请求类型 (login 或 check_in)
            use_cache: 是否使用缓存
            
        Returns:
            RecommendationResponse: 推荐结果
        """
        # 尝试从缓存获取
        if use_cache:
            cached = self._get_cached_recommendation(user_id)
            if cached:
                logger.info("Returning cached recommendation for user: {}", user_id)
                return cached
        
        # 构建请求
        request = self._build_recommendation_request(db, user_id, request_type)
        
        # 调用模型服务
        logger.info("Calling model service for user: {}, type: {}", user_id, request_type)
        recommendation = await self._call_model_service(request)
        
        # 缓存结果
        self._cache_recommendation(user_id, recommendation)
        
        logger.info("Recommendation generated for user: {}", user_id)
        return recommendation
    
    async def refresh_recommendation(
        self,
        db: Session,
        user_id: str
    ) -> RecommendationResponse:
        """
        刷新推荐（打卡后调用，不使用缓存）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            RecommendationResponse: 刷新后的推荐结果
        """
        return await self.get_recommendation(
            db=db,
            user_id=user_id,
            request_type="check_in",
            use_cache=False
        )


# 创建全局推荐服务实例
recommendation_service = RecommendationService()
