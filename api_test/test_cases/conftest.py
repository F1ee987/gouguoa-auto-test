"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 15:01
"""
from typing import Generator, Dict, Tuple
import pytest
from config.conf import HOME, LOGIN_URL, CAPTCHA_URL
from utils import Reader, DataBaseConnection, RequestHandle, Logger, CaptchaSolver

# ---------- 私有辅助函数 ----------
def _login_session(csv_row_index: int,
                   logger: Logger,
                   captcha_text: Tuple[int, RequestHandle]
                ) -> RequestHandle:
    """
    通用登录函数：读取 CSV 指定行的账号密码，识别验证码并登录，返回会话对象
    :param csv_row_index: CSV 文件中的行索引（0-based）
    :return: 已登录的 RequestHandle 实例
    """
    reader = Reader()

    # 读取账号信息
    logger.info(f"读取第 {csv_row_index + 1} 行账号信息...")
    account_data = reader.read_csv(f"{HOME}/config/accounts.csv")[csv_row_index]
    captcha_value, sess = captcha_text

    # 构造登录请求
    login_data: Dict[str, str|int]= {
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
def normal_api_login(logger: Logger,
                     api_captcha
                     ) -> Generator[RequestHandle]:
    """
    使用普通员工用户登录（CSV 第5行，索引4）
    """
    sess = _login_session(csv_row_index=4, logger=logger, captcha_text=api_captcha)   # 普通员工所在行
    yield sess
    sess.close()

@pytest.fixture(scope='function')
def hr_api_login(logger: Logger,
                 api_captcha
                    ) -> Generator[RequestHandle]:
    """
    使用人力资源用户登录（CSV 第3行，索引2）
    """
    sess = _login_session(csv_row_index=2, logger=logger, captcha_text=api_captcha)   # 人力资源所在行
    yield sess
    sess.close()

@pytest.fixture(scope='function')
def admin_api_login(logger: Logger,
                    api_captcha
                    ) -> Generator[RequestHandle]:
    """
    使用管理员用户登录（CSV 第2行，索引1）
    """
    sess = _login_session(csv_row_index=1, logger=logger, captcha_text=api_captcha)   # 管理员所在行
    yield sess
    sess.close()

@pytest.fixture(scope='session')
def db_connect(logger: Logger) -> Generator[DataBaseConnection]:
    """
    数据库连接
    """
    conn = DataBaseConnection(logger)
    yield conn
    conn.close()

@pytest.fixture(scope='function')
def api_captcha() -> Generator[Tuple[int, RequestHandle]]:
    """api测试获取验证码文本"""
    solver = CaptchaSolver()
    session = RequestHandle(True)
    captcha_res = session.get(CAPTCHA_URL, timeout=5)
    captcha_path = f"{HOME}/utils/captcha_temp.png"
    with open(captcha_path, "wb") as f:
        f.write(captcha_res.content)
    captcha = solver.solve(captcha_path)
    yield captcha, session
    session.close()