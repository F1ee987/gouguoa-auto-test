"""
接口测试夹具：提供已登录会话、验证码、数据库连接等可复用资源。
"""
from typing import Generator, Tuple
import pytest
from config.conf import CAPTCHA_DIR, DB
from utils import (
    DataBaseConnection,
    Logger,
    RequestHandle,
    delete_cache,
    fetch_captcha,
    load_accounts,
    login_via_session,
    solve_captcha,
    get_account_by_role
)


def _login_as(role: str, logger: Logger, captcha_session: Tuple[int, RequestHandle]) -> RequestHandle:
    """通用登录：按角色读取账号并提交登录，返回已登录会话。

    Args:
        role: 角色名（staff / hr / admin）。
        logger: 日志记录器。
        captcha_session: (验证码计算结果, 会话对象) 二元组。
    """
    account = get_account_by_role(load_accounts(), role)
    captcha_value, session = captcha_session
    return login_via_session(session, account.get('username'), account.get('password'), captcha_value)


@pytest.fixture(scope='function')
def normal_api_login(logger: Logger, api_captcha: Tuple[int, RequestHandle]) -> Generator[RequestHandle]:
    """以普通员工身份登录，返回已登录会话。"""
    session = _login_as("staff", logger, api_captcha)
    yield session
    session.close()


@pytest.fixture(scope='function')
def hr_api_login(logger: Logger, api_captcha: Tuple[int, RequestHandle]) -> Generator[RequestHandle]:
    """以人事经理身份登录，返回已登录会话。"""
    session = _login_as("hr_manager", logger, api_captcha)
    yield session
    session.close()


@pytest.fixture(scope='function')
def admin_api_login(logger: Logger, api_captcha: Tuple[int, RequestHandle]) -> Generator[RequestHandle]:
    """以管理员身份登录，返回已登录会话。"""
    session = _login_as("boss", logger, api_captcha)
    yield session
    session.close()


@pytest.fixture(scope='session')
def db_connect(logger: Logger) -> Generator[DataBaseConnection]:
    """数据库连接（会话级复用，连接一次，测试结束统一关闭）。"""
    connection = DataBaseConnection(logger)
    connection.connect(**DB)
    yield connection
    connection.close()


@pytest.fixture(scope='function')
def api_captcha() -> Generator[Tuple[int, RequestHandle]]:
    """获取验证码：下载图片、OCR 识别，返回 (计算结果, 会话)。"""
    session = RequestHandle(use_session=True)
    image_path = str(CAPTCHA_DIR / "captcha_temp.png")
    fetch_captcha(session, image_path)
    captcha_value = solve_captcha(image_path)
    yield captcha_value, session
    delete_cache(image_path)
    session.close()
