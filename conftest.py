"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 15:01
"""
import pytest
from time import time

@pytest.fixture(scope='session',autouse=True)
def timer():
    start_time: float = time()
    print("开始运行>>")
    yield
    end_time: float = time()
    print(f"运行总时长>>{end_time-start_time:.5f} seconds",flush=True)