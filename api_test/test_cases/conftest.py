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
from config.conf import HOME, LOGIN_URL, BASE_URL, DB
from utils import Reader, CaptchaSolver, DataBaseConnection, RequestHandle

@pytest.fixture(scope='function')
def db_connect() -> Generator[DataBaseConnection]:
    conn = DataBaseConnection()
    yield conn
    conn.close()

@pytest.fixture(scope='module')
def admin_api_login() -> Generator[RequestHandle]:
    read = Reader()
    capt = CaptchaSolver()
    sess = RequestHandle(True)
    admin_data = read.read_csv(f"{HOME}/config/accounts.csv")[1]
    res =sess.get( f"{BASE_URL}/captcha.html?t={int(time()*1000)}", timeout=5)
    img = f"{HOME}/utils/captcha_temp.png"
    with open(img, 'wb') as f:
        f.write(res.content)
    login_data = {
        'username': admin_data[1],
        'password': admin_data[2],
        'captcha': capt.calc_captcha(capt.clean_captcha_text(capt.ocr_captcha_image(img)))
    }
    res = sess.post(LOGIN_URL, data=login_data)
    print(res.json())
    assert res.json().get('msg') == "登录成功", f"连接失败"
    print("✔连接成功")
    yield sess
    print("✔关闭连接...")
    sess.close()