"""
UI 登录测试：驱动浏览器走完登录页面流程，并按预期结果校验跳转后的 URL。

数据来源：config/accounts.csv（由 prepare_account 解析为参数化数据）。
预期约定：expected_code=0 表示登录成功（留在首页），=1 表示登录失败（仍在登录页）。
"""
import pytest
from selenium.common import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
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

        # try:
        #     login_page.ec_wait('xpath',
        #                        '//*[@id="GouguApp"]/div/div[1]/div[2]/span[6]/ul/li/dl/dd[3]',
        #                        timeout=0.5,
        #                        poll_frequency=0.1
        #     )
        #     login_success = True
        # except TimeoutException:
        #     login_success = False
        login_page.force_wait(1.5)
        current_url = login_page.current_url
        login_success = "/home/login/index.html" not in current_url

        expected_success = (expected_code == '0')
        if expected_success and not login_success:
            raise Exception("❌ 登录失败，期望成功但实际失败。")
        elif not expected_success and login_success:
            raise Exception("❌ 登录成功，期望失败但实际成功。")
        else:
            logger.info(f"✅ 登录断言通过，用户名: {username}, 预期结果: {'成功' if expected_success else '失败'}, 实际结果: {'成功' if login_success else '失败'}。")