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

# chromedriver 查找顺序：先看环境变量，再看几个常见安装位置
# 目的：避免 Selenium Manager 每次启动都去外网查版本匹配，内网环境下能卡很久
_DEFAULT_DRIVER_CANDIDATES = (
    "D:/Python314/chromedriver.exe",
    "C:/Windows/chromedriver.exe",
)


def _resolve_chromedriver() -> str | None:
    """找本地的 chromedriver，找不到就返回 None，让 Selenium 自己处理。"""
    env_path = os.getenv("GOUGUOA_CHROMEDRIVER")
    if env_path and Path(env_path).is_file():
        return env_path
    for candidate in _DEFAULT_DRIVER_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return None


@pytest.fixture(scope='session')
def driver():
    """启动 Chrome，session 级复用，测试结束自动 quit。"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # 别加 --blink-settings=imagesEnabled=false，验证码截图会变空白，OCR 直接废
    chrome_options.add_argument('--disable-background-timer-throttling')

    # 页面加载策略：默认 eager（DOM 就绪就返回，不傻等图片/css）
    # 所有元素交互靠显式等待兜底，比 normal 快 1~2s/页
    # 如果遇到页面渲染不稳定，设环境变量 GOUGUOA_PAGE_LOAD_STRATEGY=normal 回退
    chrome_options.page_load_strategy = os.getenv(
        "GOUGUOA_PAGE_LOAD_STRATEGY", "eager"
    )

    driver_path = _resolve_chromedriver()
    if driver_path:
        print(f"使用本地 chromedriver: {driver_path}")
        browser = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    else:
        print("没找到本地 chromedriver，交给 Selenium Manager 自己找（可能慢）")
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
