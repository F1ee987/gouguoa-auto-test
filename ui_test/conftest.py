"""
UI 测试夹具：提供浏览器驱动实例（会话级复用，测试结束自动退出）。
"""
import os
from pathlib import Path
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.pages import LoginPage

# 登录账号集中维护：页面对象筛选待办数据时要用到同一个 username
STAFF_ACCOUNT = ("zhousha", "123456")
HR_ACCOUNT = ("renshi", "123456")

# chromedriver 候选位置：命中即直接使用，避免每次启动都联网解析版本
_DEFAULT_DRIVER_CANDIDATES = (
    "D:/Python314/chromedriver.exe",
    "C:/Windows/chromedriver.exe",
)


def _resolve_chromedriver() -> str | None:
    """解析本地 chromedriver 路径，找不到返回 None（交由 Selenium 自行处理）。

    不指定路径时 Selenium Manager 每次启动都会请求 googlechromelabs 查询匹配版本，
    在内网 / 代理环境下会长时间阻塞直至超时，是脚本「莫名很慢」的常见根因。
    """
    env_path = os.getenv("GOUGUOA_CHROMEDRIVER")
    if env_path and Path(env_path).is_file():
        return env_path
    for candidate in _DEFAULT_DRIVER_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return None


@pytest.fixture(scope='session')
def driver():
    """启动 Chrome 浏览器，测试结束后自动退出。"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 启用无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # 注意：不要加 --blink-settings=imagesEnabled=false。
    # 验证码是 <img>，禁用图片后元素截图为空白，OCR 必然失败。
    chrome_options.add_argument('--disable-background-timer-throttling')
    # 等 DOMContentLoaded 就返回，不等图片/样式等子资源加载完。
    # 页面元素一律由显式等待兜底，可省掉每页 1~2s 的资源加载等待。
    # 若发现页面渲染不稳定，用 GOUGUOA_PAGE_LOAD_STRATEGY=normal 回退，无需改代码。
    chrome_options.page_load_strategy = os.getenv(
        "GOUGUOA_PAGE_LOAD_STRATEGY", "eager"
    )

    driver_path = _resolve_chromedriver()
    if driver_path:
        print(f"使用本地 chromedriver: {driver_path}")
        browser = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    else:
        print("未找到本地 chromedriver，交由 Selenium Manager 解析（可能较慢）")
        browser = webdriver.Chrome(options=chrome_options)

    browser.set_page_load_timeout(30)
    yield browser
    browser.quit()

@pytest.fixture(scope='function')
def logged_staff_driver(driver: WebDriver):
    """返回已登录状态下的页面,基于普通员工登录

    Args:
        driver (WebDriver): 浏览器驱动

    Yields:
        _type_: 已登录页面
    """
    login_page = LoginPage(driver)
    login_page.login(*STAFF_ACCOUNT)
    yield driver

@pytest.fixture(scope='function')
def logged_hr_driver(driver: WebDriver):
    """返回已登录状态下的页面,基于hr登录
    Args:
        driver (WebDriver): 浏览器驱动

    Yields:
        _type_: 已登录页面
    """
    login_page = LoginPage(driver)
    login_page.login(*HR_ACCOUNT)
    yield driver
