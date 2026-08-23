"""
接口登录鉴权辅助：拉取验证码、OCR 识别、提交登录。

把原先散落在 test_api_login 与 conftest._login_session 中的
「下载验证码 -> 识别 -> 提交登录」流程收敛为可复用的函数，
供接口测试用例与夹具统一调用。
"""
from pathlib import Path
from typing import Tuple

import requests

from config.conf import CAPTCHA_DIR, LOGIN_URL, get_captcha_url
from utils.captcha_solver import CaptchaSolver
from utils.logger import Logger
from utils.request_util import RequestHandle

logger = Logger(__name__)


def fetch_captcha(session: RequestHandle, save_path: str) -> str:
    """从验证码接口下载图片并保存到本地，返回保存路径。

    Args:
        session: 当前请求会话（RequestHandle）。
        save_path: 图片保存路径。
    Returns:
        图片保存路径。
    """
    CAPTCHA_DIR.mkdir(parents=True, exist_ok=True)
    response = session.get(get_captcha_url(), timeout=5)
    with open(save_path, 'wb') as fp:
        fp.write(response.content)
    return save_path


def solve_captcha(image_path: str) -> int:
    """识别验证码图片并返回算式计算结果。"""
    return CaptchaSolver().solve(image_path)


def submit_login(
    session: RequestHandle,
    username: str,
    password: str,
    captcha: int | str,
) -> requests.Response:
    """使用账号密码与验证码提交登录，返回响应对象。"""
    login_payload = {
        'username': username,
        'password': password,
        'captcha': str(captcha),
    }
    return session.post(LOGIN_URL, data=login_payload)


def login_via_session(
    session: RequestHandle,
    username: str,
    password: str,
    captcha: int | str,
) -> RequestHandle:
    """提交登录并断言成功（服务端 msg 必须为 '登录成功'），返回已登录会话。

    适用于「预期登录成功」的夹具场景（普通员工 / 人事 / 管理员）。
    """
    response = submit_login(session, username, password, captcha)
    body = response.json()
    assert body.get('msg') == '登录成功', f"登录失败: {body}"
    logger.info("登录成功")
    return session
