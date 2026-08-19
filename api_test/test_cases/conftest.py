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
from config.conf import HOME, LOGIN_URL, BASE_URL
from utils import Reader, CaptchaSolver, DataBaseConnection, RequestHandle

@pytest.fixture(scope='session')
def db_connect(logger) -> Generator[DataBaseConnection]:
    conn = DataBaseConnection(logger)
    yield conn
    conn.close()

# ---------- 私有辅助函数 ----------
def _login_session(csv_row_index: int, logger) -> RequestHandle:
    """
    通用登录函数：读取 CSV 指定行的账号密码，识别验证码并登录，返回会话对象
    :param csv_row_index: CSV 文件中的行索引（0-based）
    :return: 已登录的 RequestHandle 实例
    """
    reader = Reader()
    capt = CaptchaSolver()
    sess = RequestHandle(True)

    # 读取账号信息
    logger.info(f"读取第 {csv_row_index + 1} 行账号信息...")
    account_data = reader.read_csv(f"{HOME}/config/accounts.csv")[csv_row_index]

    # 获取验证码图片
    captcha_url = f"{BASE_URL}/captcha.html?t={int(time() * 1000)}"
    res = sess.get(captcha_url, timeout=5)
    img_path = f"{HOME}/utils/captcha_temp.png"
    with open(img_path, 'wb') as f:
        f.write(res.content)

    # 识别验证码
    ocr_text = capt.ocr_captcha_image(img_path)
    cleaned_text = capt.clean_captcha_text(ocr_text)
    captcha_value = capt.calc_captcha(cleaned_text)

    # 构造登录请求
    login_data = {
        'username': account_data[1],
        'password': account_data[2],
        'captcha': captcha_value,
    }
    login_res = sess.post(LOGIN_URL, data=login_data)
    assert login_res.json().get('msg') == "登录成功", logger.error("登录失败")
    logger.info("登录成功")
    return sess


# ---------- 公开 Fixture ----------

@pytest.fixture(scope='function')
def normal_api_login(logger) -> Generator[RequestHandle, None, None]:
    """
    使用普通员工用户登录（CSV 第5行，索引4）
    """
    sess = _login_session(csv_row_index=4, logger=logger)   # 普通员工所在行
    yield sess
    print("✔关闭连接...")
    sess.close()


@pytest.fixture(scope='function')
def admin_api_login(logger) -> Generator[RequestHandle, None, None]:
    """
    使用管理员用户登录（CSV 第2行，索引1）
    """
    sess = _login_session(csv_row_index=1, logger=logger)   # 管理员所在行
    yield sess
    print("✔关闭连接...")
    sess.close()