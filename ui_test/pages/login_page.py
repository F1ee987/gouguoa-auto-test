"""
登录页面对象（UI 层）：封装「打开页面 -> 定位元素 -> 识别验证码 -> 填写并提交」的完整流程。
"""
from selenium.webdriver.remote.webdriver import WebDriver
from config.conf import BASE_URL, CAPTCHA_DIR
from utils import CaptchaSolver, delete_cache
from ui_test.pages import BasePage


class LoginPage(BasePage):
    """登录页操作封装。"""

    LOGIN_PAGE_URL = f"{BASE_URL}/home/login/index.html"
    CAPTCHA_IMAGE_NAME = "login_captcha.png"
    # 页面上验证码 <img> 的定位（相对 gougu-login 容器）
    CAPTCHA_IMG_XPATH = '//*[@id="gougu-login"]/div[3]/div[2]/img'

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.solver = CaptchaSolver()  # 验证码识别器

    def login(self, username: str, password: str, retries: int = 3) -> None:
        """执行完整登录流程。

        Args:
            username: 登录账号。
            password: 登录密码。
            retries: 最大尝试次数。验证码 OCR 偶发识别失败时刷新验证码重试，
                     避免个别噪点导致整条用例失败。
        """
        for attempt in range(1, retries + 1):
            try:
                self._do_login(username, password)
                return
            except Exception as error:
                if attempt == retries:
                    raise
                print(f"⚠️ 第 {attempt} 次登录失败（{error}），刷新验证码重试")

    def _do_login(self, username: str, password: str) -> None:
        """单次登录尝试：打开页面 -> 识别验证码 -> 填写并提交。"""
        self.open(self.LOGIN_PAGE_URL)

        # 等待关键元素出现
        username_input = self.wait_present("name", "username")
        password_input = self.wait_present("name", "password")
        captcha_input = self.wait_present("name", "captcha")
        login_button = self.wait_present("xpath", "//*[@id='login-submit']")

        if not all([username_input, password_input, captcha_input, login_button]):
            raise Exception("❌ 登录页面元素未找到，无法执行登录操作。")

        # 截取页面验证码图片用于 OCR
        captcha_element = self.find_element("xpath", self.CAPTCHA_IMG_XPATH)
        image_path = str(CAPTCHA_DIR / self.CAPTCHA_IMAGE_NAME)
        self.screenshot(image_path, captcha_element)

        # 填写账号密码（模拟人工输入）
        self.send_keys(element=username_input, keys=username, input_wait=True)
        self.send_keys(element=password_input, keys=password, input_wait=True)

        # 识别验证码（可能失败），无论成功与否都清理临时图片
        try:
            captcha_value = str(self.solver.solve(image_path))
        except Exception:
            self.screenshot(f"login_{username}_captcha_failed")
            raise Exception("❌ 验证码识别失败，无法执行登录操作。")
        finally:
            delete_cache(image_path)

        # 提交登录
        self.send_keys(element=captcha_input, keys=captcha_value)
        self.click(element=login_button)