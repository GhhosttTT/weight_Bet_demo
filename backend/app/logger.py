"""
日志配置
"""
import sys
from loguru import logger
from app.config import settings

# 移除默认处理器
logger.remove()

# 添加控制台输出（包括 stdout 和 stderr）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

# 添加文件输出
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    rotation="100 MB",
    retention="30 days",
    compression="zip"
)


def get_logger():
    """获取日志记录器"""
    return logger
