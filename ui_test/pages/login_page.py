"""
@Project:gouguoa-auto-test
@File   :login_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/19 13:22
"""
from . import BasePage
from selenium.webdriver.remote.webdriver import WebDriver
from config.conf import BASE_URL
from utils import CaptchaSolver, del_cache

class LoginPage(BasePage):
    """登录页面操作"""
    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.solver = CaptchaSolver()  # 初始化验证码识别器

    def login(self, username: str, password: str) -> None:
        """执行登录操作

        Args:
            username (str): 用户名
            password (str): 密码
        """
        self.open(f"{BASE_URL}/home/login/index.html")
        username_input = self.ec_wait("name", "username")
        password_input = self.ec_wait("name", "password")
        captcha_input = self.ec_wait("name", "captcha")
        login_button = self.ec_wait("xpath", "//*[@id='login-submit']")

        captcha_text = self.find_element("xpath", '//*[@id="gougu-login"]/div[3]/div[2]/img')
        self.screenshot("login_captcha.png", captcha_text)

        if not all([username_input, password_input, captcha_input, login_button]):
            raise Exception("登录页面元素未找到，无法执行登录操作。")

        self.send_keys(username_input, keys=username, input_wait=True)
        self.send_keys(password_input, keys=password, input_wait=True)

        CAPTCHA_IMG = "login_captcha.png"
        # 2. 识别验证码（可能失败）
        try:
            captcha = str(self.solver.solve(CAPTCHA_IMG))
        except Exception as e:
            print(f"验证码识别失败: {e}")
            self.screenshot(f"login_{username}_captcha_failed")
            raise Exception("验证码识别失败，无法执行登录操作。")  # 重新抛出异常以便捕获和处理
        finally:
            del_cache(CAPTCHA_IMG)

        # 3. 执行登录操作
        self.send_keys(captcha_input, keys=captcha)
        self.click(login_button)
        self.force_wait(2)