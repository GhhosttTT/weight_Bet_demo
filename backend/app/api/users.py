"""
用户 API 路由
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.services.friend_search_service import FriendSearchService
from app.services.audit_service import AuditService
from app.middleware.auth import get_current_user_id
from pydantic import BaseModel

router = APIRouter()


@router.get("/search")
def search_friend_by_email(
    email: str = Query(..., description="好友邮箱地址"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    通过邮箱搜索好友
    
    - **email**: 好友邮箱地址
    
    返回用户的基本公开信息（姓名、年龄、性别）
    """
    result = FriendSearchService.search_by_email(db, email)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "user_id": result.user_id,
        "nickname": result.nickname,
        "age": result.age,
        "gender": result.gender
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户信息
    
    - **user_id**: 用户 ID
    
    注意: 只能查看自己的信息
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看其他用户信息"
        )
    
    return UserService.get_user_profile(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: str,
    update_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    - **user_id**: 用户 ID
    - **update_data**: 更新数据
    """
    return UserService.update_user_profile(db, user_id, current_user_id, update_data)


class BindPaymentMethodRequest(BaseModel):
    """绑定支付方式请求"""
    payment_method_id: str


@router.post("/{user_id}/payment-methods", response_model=UserResponse)
def bind_payment_method(
    user_id: str,
    request: BindPaymentMethodRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    绑定支付方式
    
    - **user_id**: 用户 ID
    - **payment_method_id**: 支付方式 ID
    """
    return UserService.bind_payment_method(
        db, 
        user_id, 
        current_user_id, 
        request.payment_method_id
    )



@router.get("/{user_id}/export")
def export_user_data(
    user_id: str,
    request: Request,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    导出用户所有数据
    
    - **user_id**: 用户 ID
    
    注意: 只能导出自己的数据
    
    返回包含所有用户数据的 JSON 文件
    """
    # 记录审计日志
    AuditService.log_from_request(
        db=db,
        request=request,
        action="user.export_data",
        resource_type="user",
        user_id=current_user_id,
        resource_id=user_id
    )
    
    export_data = UserService.export_user_data(db, user_id, current_user_id)
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{user_id}.json"
        }
    )


@router.delete("/{user_id}")
def delete_user_account(
    user_id: str,
    request: Request,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除或匿名化用户账户
    
    - **user_id**: 用户 ID
    
    注意: 
    - 只能删除自己的账户
    - 不能有进行中的对赌计划
    - 不能有冻结资金
    """
    # 记录审计日志
    AuditService.log_from_request(
        db=db,
        request=request,
        action="user.delete_account",
        resource_type="user",
        user_id=current_user_id,
        resource_id=user_id
    )
    
    UserService.delete_user_account(db, user_id, current_user_id)
    
    return {"message": "账户已成功删除"}


class AuditLogQuery(BaseModel):
    """审计日志查询参数"""
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


@router.post("/{user_id}/audit-logs")
def query_audit_logs(
    user_id: str,
    query: AuditLogQuery,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    查询用户的审计日志
    
    - **user_id**: 用户 ID
    - **query**: 查询参数
    
    注意: 只能查询自己的审计日志
    """
    # 权限验证
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查询其他用户的审计日志"
        )
    
    logs = AuditService.query_logs(
        db=db,
        user_id=user_id,
        action=query.action,
        resource_type=query.resource_type,
        start_date=query.start_date,
        end_date=query.end_date,
        limit=query.limit,
        offset=query.offset
    )
    
    return {
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "total": len(logs),
        "limit": query.limit,
        "offset": query.offset,
    }
