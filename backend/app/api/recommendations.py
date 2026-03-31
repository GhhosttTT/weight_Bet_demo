"""
推荐功能 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import recommendation_service
from app.middleware.auth import get_current_user_id
from app.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/", response_model=RecommendationResponse)
async def get_recommendation(
    current_user_id: str = Depends(get_current_user_id),
    use_cache: bool = Query(True, description="是否使用缓存"),
    db: Session = Depends(get_db)
):
    """
    获取今日推荐（登录时调用）
    
    返回个性化的运动和饮食推荐
    """
    logger.info("Getting recommendation for user: {}", current_user_id)
    return await recommendation_service.get_recommendation(
        db=db,
        user_id=current_user_id,
        request_type="login",
        use_cache=use_cache
    )


@router.post("/refresh", response_model=RecommendationResponse)
async def refresh_recommendation(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    刷新推荐（打卡后调用，不使用缓存）
    
    打卡后应该调用此接口获取最新的推荐
    """
    logger.info("Refreshing recommendation for user: {}", current_user_id)
    return await recommendation_service.refresh_recommendation(
        db=db,
        user_id=current_user_id
    )
