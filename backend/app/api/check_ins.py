"""
打卡相关的 API 路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.services.check_in_service import CheckInService
from app.schemas.check_in import (
    CreateCheckInRequest,
    ReviewCheckInRequest,
    CheckInResponse,
    ProgressStats,
    UploadPhotoRequest
)

router = APIRouter()


@router.post("/check-ins", response_model=CheckInResponse, status_code=201)
def create_check_in(
    request: CreateCheckInRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    创建打卡记录
    
    - **plan_id**: 计划 ID
    - **weight**: 体重 (30-300 kg)
    - **check_in_date**: 打卡日期
    - **photo_url**: 体重秤照片 URL (可选)
    - **note**: 备注 (可选)
    """
    return CheckInService.create_check_in(db, current_user_id, request)


@router.post("/check-ins/{check_in_id}/photo", response_model=CheckInResponse)
def upload_photo(
    check_in_id: str,
    request: UploadPhotoRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    上传体重秤照片
    
    - **check_in_id**: 打卡记录 ID
    - **photo_url**: 照片 URL
    """
    return CheckInService.upload_photo(db, current_user_id, check_in_id, request.photo_url)


@router.post("/check-ins/{check_in_id}/review", response_model=CheckInResponse)
def review_check_in(
    check_in_id: str,
    request: ReviewCheckInRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    审核打卡记录
    
    - **check_in_id**: 打卡记录 ID
    - **review_status**: 审核状态 (approved/rejected)
    - **review_comment**: 审核意见 (可选)
    """
    return CheckInService.review_check_in(db, check_in_id, current_user_id, request)


@router.get("/check-ins/plan/{plan_id}/user/{user_id}", response_model=List[CheckInResponse])
def get_check_in_history(
    plan_id: str,
    user_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取打卡历史
    
    - **plan_id**: 计划 ID
    - **user_id**: 用户 ID
    - **limit**: 返回数量限制 (默认 100)
    - **offset**: 偏移量 (默认 0)
    """
    return CheckInService.get_check_in_history(db, plan_id, user_id, limit, offset)


@router.get("/check-ins/plan/{plan_id}/progress", response_model=ProgressStats)
def get_progress(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取进度统计
    
    - **plan_id**: 计划 ID
    
    返回当前用户在该计划中的进度统计
    """
    return CheckInService.get_progress(db, plan_id, current_user_id)
