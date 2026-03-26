"""
全局错误处理中间件
"""
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.logger import get_logger
import traceback
from datetime import datetime

logger = get_logger()


def create_error_response(
    error_type: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: dict = None
) -> JSONResponse:
    """
    创建统一的错误响应格式
    
    Args:
        error_type: 错误类型
        message: 错误消息
        status_code: HTTP 状态码
        details: 额外的错误详情
        
    Returns:
        JSONResponse: 统一格式的错误响应
    """
    content = {
        "error": error_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        content["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 异常"""
    logger.warning(
        "HTTP exception: {} - {}",
        exc.status_code,
        exc.detail,
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return create_error_response(
        error_type="HTTP Error",
        message=exc.detail,
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    # 将错误转换为字符串，避免 loguru 格式化问题
    error_details = str(exc.errors())
    logger.error(
        "Validation error: {}",
        error_details,
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    return create_error_response(
        error_type="Validation Error",
        message="请求参数验证失败",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": exc.errors()}
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库错误"""
    logger.error(
        "Database error: {}",
        str(exc),
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        },
        exc_info=True
    )
    
    return create_error_response(
        error_type="Database Error",
        message="数据库操作失败",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


async def general_exception_handler(request: Request, exc: Exception):
    """处理通用错误 - 捕获所有未处理的异常"""
    # 记录完整的错误堆栈
    error_traceback = traceback.format_exc()
    
    logger.error(
        "Unhandled exception: {}",
        str(exc),
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__,
            "traceback": error_traceback
        },
        exc_info=True
    )
    
    return create_error_response(
        error_type="Internal Server Error",
        message="服务器内部错误",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
