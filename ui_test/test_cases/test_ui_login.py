"""
UI 登录测试：驱动浏览器走完登录页面流程，并按预期结果校验跳转后的 URL。

数据来源：config/accounts.csv（由 prepare_account 解析为参数化数据）。
预期约定：expected_code=0 表示登录成功（留在首页），=1 表示登录失败（仍在登录页）。
"""
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from config.conf import BASE_URL
from utils import Logger, prepare_account
from ui_test.pages import LoginPage

TEST_DATA, TEST_IDS = prepare_account()


class TestLogin:
    """UI 登录测试套件。"""

    @pytest.fixture(scope='session')
    def login_page(self, driver: WebDriver) -> LoginPage:
        """构造登录页面对象。"""
        return LoginPage(driver)

    @pytest.mark.login
    @pytest.mark.ui
    @pytest.mark.parametrize('username,password,expected_code', TEST_DATA, ids=TEST_IDS)
    def test_login(
        self,
        username: str,
        password: str,
        expected_code: str,
        login_page: LoginPage,
        logger: Logger,
    ):
        logger.info(f"正在测试, 用户名: {username}")
        login_page.login(username, password)

        if expected_code == '0':
            # 期望登录成功：URL 应为 BASE_URL
            assert login_page.current_url.rstrip('/') == BASE_URL, \
                logger.error(
                    f"❌ 登录成功断言失败，期望 URL: {BASE_URL}，实际 URL: {login_page.current_url}"
                )
            logger.info(f"✅ 登录测试通过 | 用户名={username} | 预期>>成功")
        else:
            # 期望登录失败：URL 应仍停留在登录页
            assert "/home/login/index.html" in login_page.current_url, \
                logger.error(
                    f"❌ 登录失败断言失败，期望 URL 包含: {BASE_URL}/home/login/index.html，"
                    f"实际 URL: {login_page.current_url}"
                )
            logger.info(f"✅ 登录测试通过 | 用户名={username} | 预期>>失败")
