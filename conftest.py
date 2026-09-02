"""
pytest 全局夹具（项目根级）。

提供：会话级计时器（统计总运行时长）与全局日志记录器。
"""
from time import time
from typing import Generator
import pytest
from utils import Logger, DataBaseConnection
from config.conf import DB

@pytest.fixture(scope='session', autouse=True)
def timer():
    """会话级计时器：测试前后打印总运行时长。"""
    start_time = time()
    print("开始运行>>")
    yield
    end_time = time()
    print(f"运行总时长>>{end_time - start_time:.4f} seconds", flush=True)

@pytest.fixture(scope='session')
def logger() -> Generator[Logger]:
    """全局日志记录器（会话级复用）。"""
    log = Logger(__name__)
    yield log
    print("日志记录关闭")

@pytest.fixture(scope='class')
def db_connect(logger: Logger) -> Generator[DataBaseConnection]:
    """数据库连接"""
    connection = DataBaseConnection(logger)
    connection.connect(**DB)
    yield connection
    connection.close()
