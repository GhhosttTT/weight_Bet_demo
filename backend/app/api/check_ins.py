"""
打卡相关的 API 路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.services.check_in_service import CheckInService
from app.models.betting_plan import BettingPlan
from app.models.check_in import CheckIn
from app.schemas.check_in import (
    CreateCheckInRequest,
    ReviewCheckInRequest,
    CheckInResponse,
    ProgressStats,
    UploadPhotoRequest
)

router = APIRouter()

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "checkins"
MAX_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _matches_image_signature(content: bytes, content_type: str) -> bool:
    """校验文件头，避免仅伪造 Content-Type 上传 HTML 或脚本文件。"""
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    }
    return signatures.get(content_type, False)


def _public_photo_url(response: CheckInResponse) -> CheckInResponse:
    """不向客户端暴露存储路径，统一返回受保护的读取接口。"""
    if response.photo_url and response.photo_url.startswith("/uploads/checkins/"):
        response.photo_url = f"/api/check-ins/{response.id}/photo"
    return response


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
    return _public_photo_url(CheckInService.create_check_in(db, current_user_id, request))


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
    return _public_photo_url(CheckInService.upload_photo(db, current_user_id, check_in_id, request.photo_url))


@router.post("/check-ins/{check_in_id}/photo/upload", response_model=CheckInResponse)
async def upload_photo_file(
    check_in_id: str,
    photo: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """上传图片文件，并将相对访问地址写入打卡记录。"""
    check_in = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
    if not check_in:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡记录不存在")
    if check_in.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改此打卡记录")

    extension = ALLOWED_PHOTO_TYPES.get(photo.content_type or "")
    if extension is None:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="仅支持 JPG、PNG 或 WebP 图片")

    content = await photo.read(MAX_PHOTO_BYTES + 1)
    if len(content) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="图片不能超过 5MB")
    if not _matches_image_signature(content, photo.content_type or ""):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="图片内容与声明类型不匹配")

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{check_in_id}_{uuid.uuid4().hex}{extension}"
    (UPLOAD_ROOT / filename).write_bytes(content)
    return _public_photo_url(CheckInService.upload_photo(
        db, current_user_id, check_in_id, f"/uploads/checkins/{filename}"
    ))


@router.get("/check-ins/{check_in_id}/photo")
def get_photo_file(
    check_in_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """按计划参与权限读取打卡照片，禁止公开静态访问。"""
    check_in = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
    if not check_in or not check_in.photo_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡照片不存在")

    plan = db.query(BettingPlan).filter(BettingPlan.id == check_in.plan_id).first()
    is_owner = check_in.user_id == current_user_id
    is_participant = plan and current_user_id in (plan.creator_id, plan.participant_id)
    if not is_owner and not (is_participant and check_in.review_status.value == "approved"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限查看此打卡照片")

    prefix = "/uploads/checkins/"
    if not check_in.photo_url.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡照片不存在")
    filename = check_in.photo_url[len(prefix):]
    if not filename or Path(filename).name != filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡照片不存在")
    photo_path = (UPLOAD_ROOT / filename).resolve()
    if UPLOAD_ROOT.resolve() not in photo_path.parents or not photo_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="打卡照片不存在")
    media_type = ALLOWED_PHOTO_TYPES.get(photo_path.suffix.lower(), "application/octet-stream")
    return FileResponse(photo_path, media_type=media_type)


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
    return _public_photo_url(CheckInService.review_check_in(db, check_in_id, current_user_id, request))


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
    plan = db.query(BettingPlan).filter(BettingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在")
    participant_ids = {plan.creator_id, plan.participant_id}
    if current_user_id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您不是该计划的参与者")
    if user_id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该用户不是该计划的参与者")

    history = CheckInService.get_check_in_history(
        db, plan_id, user_id, limit, offset, viewer_user_id=current_user_id
    )
    return [_public_photo_url(item) for item in history]


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
