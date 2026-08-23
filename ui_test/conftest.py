"""
UI 测试夹具：提供浏览器驱动实例（会话级复用，测试结束自动退出）。
"""
import pytest

@pytest.fixture(scope='session')
def driver():
    """启动 Chrome 浏览器，测试结束后自动退出。"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 启用无头模式
    browser = webdriver.Chrome(options=chrome_options)
    yield browser
    browser.quit()
