"""
@Project:gouguoa-auto-test
@File   :logger.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:10
"""
import logging
from pathlib import Path

class Logger:
    """日志记录器封装类"""

    def __init__(self, name: str, level: str = 'DEBUG', log_file: str | None = None):
        self._logger = logging.getLogger(name)

        # 校验并设置级别
        level_upper = level.upper()
        if not hasattr(logging, level_upper):
            raise ValueError(f"Invalid log level: {level}")
        self._logger.setLevel(getattr(logging, level_upper))

        if not self._logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self._logger.addHandler(stream_handler)

            # 文件（可选）
            if log_file and log_file.strip():
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)

            # 关键：防止重复输出
            self._logger.propagate = False

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别字符串
        """
        log_level = getattr(logging, level.upper(), logging.DEBUG)
        self._logger.setLevel(log_level)
        for handler in self._logger.handlers:
            handler.setLevel(log_level)

    def debug(self, msg: str):
        """输出 DEBUG 级别日志"""
        self._logger.debug(msg)

    def info(self, msg: str):
        """输出 INFO 级别日志"""
        self._logger.info(msg)

    def warning(self, msg: str):
        """输出 WARNING 级别日志"""
        self._logger.warning(msg)

    def error(self, msg: str):
        """输出 ERROR 级别日志"""
        self._logger.error(msg)

    def critical(self, msg: str):
        """输出 CRITICAL 级别日志"""
        self._logger.critical(msg)