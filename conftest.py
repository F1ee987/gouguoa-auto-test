"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 13:48
"""
from time import time
import pytest

@pytest.fixture(scope='session',autouse=True)
def timer():
    start_time: float = time()
    print("开始运行>>")
    yield
    end_time: float = time()
    print(f"运行总时长>>{end_time-start_time:.5f} seconds",flush=True)