"""
接口测试夹具：提供已登录会话、验证码、数据库连接等可复用资源。

账号与角色映射（config/accounts.csv 行索引，0-based 含表头）：
    - 普通员工 staff   -> 索引 4
    - 人事经理 hr      -> 索引 2
    - 管理员 admin     -> 索引 1
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
)

# 角色 -> accounts.csv 行索引（避免在各夹具中散落魔法数字）
_ACCOUNT_ROW_INDEX = {
    "staff": 4,
    "hr": 2,
    "admin": 1,
}


def _login_as(role: str, logger: Logger, captcha_session: Tuple[int, RequestHandle]) -> RequestHandle:
    """通用登录：按角色读取账号并提交登录，返回已登录会话。

    Args:
        role: 角色名（staff / hr / admin），对应 _ACCOUNT_ROW_INDEX。
        logger: 日志记录器。
        captcha_session: (验证码计算结果, 会话对象) 二元组。
    """
    accounts = load_accounts()
    row_index = _ACCOUNT_ROW_INDEX[role]
    account = accounts[row_index]
    captcha_value, session = captcha_session
    return login_via_session(session, account[1], account[2], captcha_value)


@pytest.fixture(scope='function')
def normal_api_login(logger: Logger, api_captcha: Tuple[int, RequestHandle]) -> Generator[RequestHandle]:
    """以普通员工身份登录，返回已登录会话。"""
    session = _login_as("staff", logger, api_captcha)
    yield session
    session.close()


@pytest.fixture(scope='function')
def hr_api_login(logger: Logger, api_captcha: Tuple[int, RequestHandle]) -> Generator[RequestHandle]:
    """以人事经理身份登录，返回已登录会话。"""
    session = _login_as("hr", logger, api_captcha)
    yield session
    session.close()


@pytest.fixture(scope='function')
def admin_api_login(logger: Logger, api_captcha: Tuple[int, RequestHandle]) -> Generator[RequestHandle]:
    """以管理员身份登录，返回已登录会话。"""
    session = _login_as("admin", logger, api_captcha)
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
