"""
UI 测试夹具：提供浏览器驱动实例（会话级复用，测试结束自动退出）。
"""
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from ui_test.pages import LoginPage

@pytest.fixture(scope='session')
def driver():
    """启动 Chrome 浏览器，测试结束后自动退出。"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 启用无头模式
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5)
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
    login_page.login("zhousha", "123456")
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
    login_page.login("renshi", "123456")
    yield driver
