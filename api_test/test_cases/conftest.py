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
from utils import Reader, CaptchaSolver

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
    s = CaptchaSolver()
    admin_data = r.read_csv(f"{HOME}/config/accounts.csv")[1]
    session = requests.Session()
    res =session.request('GET', f"{BASE_URL}/captcha.html?t={int(time()*1000)}", timeout=5)
    img = f"{HOME}/utils/img.png"
    with open(img, 'wb') as f:
        f.write(res.content)
    login_data = {
        'username': admin_data[1],
        'password': admin_data[2],
        'captcha': s.calc_captcha(s.clean_captcha_text(s.ocr_captcha_image(img)))
    }
    res = session.request('POST', LOGIN_URL, data=login_data)
    assert res.json().get('msg') == "登录成功", f"连接失败"
    print("✔连接成功")
    yield session
    print("✔关闭连接...")
    session.close()