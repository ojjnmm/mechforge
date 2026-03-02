#!/usr/bin/env python
"""
MechForge Work - Logger Module

统一的日志管理模块
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class MechForgeFormatter(logging.Formatter):
    """自定义日志格式化器"""

    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # 添加颜色
        if sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"

        return super().format(record)


def setup_logger(
    name: str = "mechforge",
    level: str = "INFO",
    log_file: Path | None = None,
    console: bool = True
) -> logging.Logger:
    """
    设置日志器
    
    Args:
        name: 日志器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
        console: 是否输出到控制台
    
    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 设置级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 格式
    formatter = MechForgeFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台输出
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "mechforge") -> logging.Logger:
    """
    获取日志器
    
    Args:
        name: 日志器名称
    
    Returns:
        日志器实例
    """
    return logging.getLogger(name)


# 默认日志器
_default_logger: logging.Logger | None = None


def init_logging(
    level: str = None,
    log_dir: Path = None,
    console: bool = True
) -> logging.Logger:
    """
    初始化日志系统
    
    Args:
        level: 日志级别 (默认从环境变量 LOG_LEVEL 获取)
        log_dir: 日志目录
        console: 是否输出到控制台
    
    Returns:
        根日志器
    """
    global _default_logger

    # 获取日志级别
    if level is None:
        level = os.environ.get("MECHFORGE_LOG_LEVEL", "INFO")

    # 获取日志目录
    if log_dir is None:
        log_dir = Path(os.environ.get("MECHFORGE_LOG_DIR", "./logs"))

    # 创建日志文件
    log_file = None
    if log_dir:
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"mechforge_{today}.log"

    # 设置根日志器
    _default_logger = setup_logger(
        name="mechforge",
        level=level,
        log_file=log_file,
        console=console
    )

    # 设置第三方库日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("gmsh").setLevel(logging.WARNING)

    return _default_logger


class LogContext:
    """日志上下文管理器"""

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"开始: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.info(f"完成: {self.operation} ({elapsed:.2f}s)")
        else:
            self.logger.error(f"失败: {self.operation} ({elapsed:.2f}s) - {exc_val}")

        return False  # 不抑制异常


def log_function(func):
    """函数调用日志装饰器"""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"调用: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"返回: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"异常: {func.__name__} - {e}")
            raise

    return wrapper


def log_async_function(func):
    """异步函数调用日志装饰器"""
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"调用: {func.__name__}")

        try:
            result = await func(*args, **kwargs)
            logger.debug(f"返回: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"异常: {func.__name__} - {e}")
            raise

    return wrapper


# 便捷函数
def debug(msg: str):
    """调试日志"""
    get_logger().debug(msg)


def info(msg: str):
    """信息日志"""
    get_logger().info(msg)


def warning(msg: str):
    """警告日志"""
    get_logger().warning(msg)


def error(msg: str):
    """错误日志"""
    get_logger().error(msg)


def critical(msg: str):
    """严重错误日志"""
    get_logger().critical(msg)
