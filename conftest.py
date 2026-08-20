"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 13:48
"""
from time import time
import pytest
from utils import Logger, CaptchaSolver, RequestHandle
from typing import Generator, Tuple
from config.conf import CAPTCHA_URL, HOME

@pytest.fixture(scope='session',autouse=True)
def timer():
    start_time: float = time()
    print("开始运行>>")
    yield
    end_time: float = time()
    print(f"运行总时长>>{end_time-start_time:.5f} seconds",flush=True)

@pytest.fixture(scope='session')
def logger() -> Generator[Logger]:
    log = Logger(__name__)
    yield log
    print("日志记录关闭")

@pytest.fixture(scope='function')
def captcha_text() -> Generator[Tuple[int, RequestHandle]]:
    """获取验证码文本"""
    solver = CaptchaSolver()
    session = RequestHandle(True)
    captcha_res = session.get(CAPTCHA_URL, timeout=5)
    captcha_path = f"{HOME}/utils/captcha_temp.png"
    with open(captcha_path, "wb") as f:
        f.write(captcha_res.content)
    captcha = solver.solve(captcha_path)
    yield captcha, session
    session.close()