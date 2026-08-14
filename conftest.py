"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 15:01
"""
from typing import Generator
import pytest
from time import time
import requests
from config.conf import HOME, LOGIN_URL, BASE_URL
from utils import Reader

@pytest.fixture(scope='session',autouse=True)
def timer():
    start_time: float = time()
    print("开始运行>>")
    yield
    end_time: float = time()
    print(f"运行总时长>>{end_time-start_time:.5f} seconds",flush=True)

@pytest.fixture(scope='module')
def admin_api_login() -> Generator[requests.Session]:
    r = Reader()
    admin_data = r.read_csv(f"{HOME}/config/accounts.csv")[1]
    session = requests.Session()
    session.request('GET', f"{BASE_URL}/captcha.html?t={int(time()*1000)}", timeout=5)
    login_data = {
        'username': admin_data[1],
        'password': admin_data[2],
        'captcha': ''
    }
    session.request('POST', LOGIN_URL, data=login_data)
    yield session
    session.close()