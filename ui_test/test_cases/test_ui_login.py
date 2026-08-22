import pytest
from ui_test.pages import LoginPage
from selenium.webdriver.remote.webdriver import WebDriver
from utils import prepare_account
from config.conf import BASE_URL

class TestLogin:
    @pytest.fixture(scope='session')
    def setup(self, driver: WebDriver):
        login_page = LoginPage(driver)
        yield login_page

    TEST_DATA, TEST_IDS = prepare_account()

    @pytest.mark.login
    @pytest.mark.ui
    @pytest.mark.parametrize('username,password,expected_code', TEST_DATA, ids=TEST_IDS)
    def test_login(self, username, password, expected_code, setup, logger):
        logger.info(f"正在测试,用户名: {username}")
        setup.login(username, password)
        if expected_code == '0':
            # 期望登录成功：URL 应为 BASE_URL（或具体首页路径）
            assert setup.current_url.rstrip('/') == BASE_URL, \
                logger.error(f"登录成功断言失败，期望URL: {BASE_URL}，实际URL: {setup.current_url}")
            logger.info(f"登录测试通过 | 用户名={username} | 预期>>成功")
        else:
            # 期望登录失败：URL 应包含登录页路径
            assert "/home/login/index.html" in setup.current_url, \
                logger.error(f"登录失败断言失败，期望URL包含: {BASE_URL}/home/login/index.html，实际URL: {setup.current_url}")
            logger.info(f"登录测试通过 | 用户名={username} | 预期>>失败")