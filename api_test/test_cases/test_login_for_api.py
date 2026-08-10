"""
@Project:gouguoa-auto-test
@File   :test_login_for_api.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 14:57
"""
import pytest
import requests
from config.conf import BASE_URL, LOGIN_URL, ADD_ACCOUNT_URL
from ui_test.utils.reader import Reader

def get_test_accounts():
    """读取accounts.csv文件返回测试账号数据"""
    reader = Reader()
    return reader.read_csv('../data/accounts.csv')

def prepare_account():
    """准备测试所需的账号信息"""
    accounts = get_test_accounts()
    if not accounts:
        pytest.skip("未读取到测试账号")

    test_data = []
    for i in range(1, 8):
        test_account = accounts[i]
        username = test_account[1]
        password = test_account[2]
        print(f"🚀 加载测试账号: {username}")
        test_data.append((username, password))

    return test_data

def try_brute_force_captcha(username, password):
    """尝试暴力破解验证码（增强版）"""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import random
    import time

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
            session.get(f"{BASE_URL}/captcha.html?t={int(time.time()*1000)}", timeout=5)
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

@pytest.mark.parametrize("username,password", prepare_account())
def test_login_with_brute_force(username, password):
    """暴力破解验证码"""
    try_brute_force_captcha(username, password)

# def test_add_account():
#     """"添加用户接口"""
#     res = requests.post(ADD_ACCOUNT_URL, data={})
#     print(res.text)