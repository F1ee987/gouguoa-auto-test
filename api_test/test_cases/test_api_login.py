"""
@Project:gouguoa-auto-test
@File   :test_login_for_api.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:57
"""
import pytest
import requests
import time
from config.conf import BASE_URL, LOGIN_URL, HOME, CAPTCHA_URL
from utils import CaptchaSolver, RequestHandle, Logger,prepare_account, del_cache

def try_brute_force_captcha(username: str, password: str):
    """尝试暴力破解验证码（增强版）"""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import random

    # ---------- 1. 配置 Session（含重试和连接池） ----------
    session = requests.Session()

    retry_strategy = Retry(
        total=2,                     # 最多重试 2 次
        backoff_factor=0.5,          # 重试间隔：0.5s, 1s, 2s...
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # ---------- 2. 设置请求头 ----------
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": BASE_URL + "/home/login/login_submit"
    }
    session.headers.update(headers)

    # ---------- 3. 暴力破解主循环 ----------
    login_in = False
    fail_reason = ""

    for answer in range(10, 41):   # 修正为包含 40
        login_data = {
            'username': username,
            'password': password,
            'captcha': str(answer)
        }

        # 获取新验证码（注意：这里可能也需要重试，但 Retry 已全局配置）
        try:
            session.get(CAPTCHA_URL, timeout=5)
        except Exception as e:
            print(f"⚠️ 获取验证码失败: {e}，跳过 {answer}")
            continue

        # 发送登录请求（自带重试）
        try:
            res = session.post(LOGIN_URL, data=login_data, timeout=(3.05, 5))
        except requests.exceptions.Timeout:
            print("❌ 请求超时，跳过", answer)
            continue
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}，跳过 {answer}")
            continue

        # 适当延时，模拟人工操作（关键！）
        time.sleep(random.uniform(0.5, 1.5))

        # 检查状态码
        if res.status_code != 200:
            print(f"⚠️ 请求失败，状态码: {res.status_code}，跳过 {answer}")
            continue

        msg = res.json().get("msg", "")

        # 判断验证码是否正确
        if "验证码不正确" in msg:
            continue

        print(f"✅ 验证码正确，答案: {answer}")

        # 根据 msg 内容处理
        if "该用户禁止登录" in msg:
            fail_reason = f"用户 {username} 被禁止登录"
            print(f"❌ {fail_reason}")
            break
        if "登录成功" in msg:
            login_in = True
            print("✅ 登录成功！")
            break
        else:
            fail_reason = f"未知响应: {msg}"
            print(f"❌ {fail_reason}")
            break

    # ---------- 4. 最终断言 ----------
    assert login_in, f"❌ 登录失败: {fail_reason if fail_reason else '所有验证码均未命中'}"

# @pytest.mark.api
# @pytest.mark.login
# @pytest.mark.parametrize("username,password", prepare_account())
# def test_login_with_brute_force(username, password):
#     """暴力破解验证码, 已知验证码范围"""
#     try_brute_force_captcha(username, password)

TEST_DATA, TEST_IDS = prepare_account()

@pytest.mark.api
@pytest.mark.login
@pytest.mark.parametrize("username,password,expected_code", TEST_DATA, ids=TEST_IDS)
def test_by_orc_captcha(username: str, password: str, expected_code: str, logger: Logger):
    """OCR 解码验证码, 并登录"""
    solve = CaptchaSolver()
    session = RequestHandle(True)
    captcha_res = session.get(CAPTCHA_URL, timeout=5)
    captcha_img = f"{HOME}/api_test/data/captcha_data/captcha_{username}.png"
    with open(captcha_img, 'wb') as f:
        f.write(captcha_res.content)
    #计算结果
    captcha_num = solve.solve(captcha_img)
    logger.info(f"OCR 解码验证码: {captcha_num}")

    """使用解码后的验证码登录"""
    login_data = {
        'username': username,
        'password': password,
        'captcha': str(captcha_num)
    }
    login_res = session.post(url=LOGIN_URL, data=login_data)

    assert login_res.status_code == 200, logger.error(f"响应请求错误, 当前响应码为>>{login_res.status_code}")

    try:
        response_data = login_res.json()
        actual_code = response_data.get('code')
        assert actual_code != expected_code, logger.error(
            f"预期失败，期望状态码为: {expected_code}，实际为: {actual_code}"
        )
        logger.info(f"✅ 登录信息：{response_data.get('msg')}")
    except ValueError:
        logger.error("响应内容不是有效的 JSON 格式，无法解析。")
    finally:
        del_cache(captcha_img)
        session.close()