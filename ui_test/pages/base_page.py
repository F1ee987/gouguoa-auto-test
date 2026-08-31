"""
Selenium 页面操作基类：封装元素查找、输入、点击、等待与截图等通用动作。

设计原则：
- 所有操作前校验 driver 已初始化；
- find / send_keys / click 支持「直接传入元素」或「按定位方式查找」两种用法；
- 显式等待（ec_wait）优先于强制等待（force_wait）。
"""
from datetime import datetime
from random import uniform
import os
from time import sleep
from typing import Optional
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from config.conf import PROJECT_ROOT


class BasePage:
    """基础页面操作封装。"""

    def __init__(self, driver: WebDriver) -> None:
        if not driver:
            raise ValueError("WebDriver对象不能为空")
        self._driver = driver
        self.options: Optional[Options] = None

    # --------------------------- 属性 / 配置 ---------------------------
    @property
    def title(self) -> str:
        """当前页面标题。"""
        return self._driver.title

    @property
    def current_url(self) -> str:
        """当前页面 URL。"""
        return self._driver.current_url

    def add_options(self, options: Optional[Options]) -> None:
        """附加浏览器启动选项。"""
        self.options = options

    @property
    def get_screenshot_as_png(self) -> bytes:
        return self._driver.get_screenshot_as_png()

    # --------------------------- 导航 / 等待 ---------------------------
    def open(self, url: str) -> None:
        """打开指定 URL。"""
        self._driver.get(url)

    @staticmethod
    def force_wait(seconds: float) -> None:
        """强制休眠指定秒数（仅用于无法显式等待的过渡场景）。"""
        sleep(seconds)

    # --------------------------- 显式等待 ---------------------------
    def wait_visible(self, by: str, value: str, timeout: float = 5) -> WebElement:
        """等待元素可见并返回"""
        return WebDriverWait(self._driver, timeout).until(
            EC.visibility_of_element_located((by, value)),
            message=f"元素未可见: {by}={value}，等待了 {timeout}s"
        )

    def wait_clickable(self, by: str, value: str, timeout: float = 5) -> WebElement:
        """等待元素可点击并返回"""
        return WebDriverWait(self._driver, timeout).until(
            EC.element_to_be_clickable((by, value)),
            message=f"元素不可点击: {by}={value}，等待了 {timeout}s"
        )

    def wait_present(self, by: str, value: str, timeout: float = 5) -> WebElement:
        """等待元素存在于 DOM 中（不一定可见）"""
        return WebDriverWait(self._driver, timeout).until(
            EC.presence_of_element_located((by, value)),
            message=f"元素不存在: {by}={value}，等待了 {timeout}s"
        )

    # --------------------------- 元素操作 ---------------------------
    def find_element(self, by: str, value: str) -> WebElement:
        """按定位方式查找元素（找不到由 Selenium 抛异常）。"""
        return self._driver.find_element(by, value)

    def send_keys(
        self,
        by: Optional[str] = None,
        value: Optional[str] = None,
        element: Optional[WebElement] = None,
        keys: str = '',
        input_wait: bool = False,
    ) -> None:
        """向元素输入文本。

        Args:
            element: 直接传入的目标元素（可选）。
            by: 元素定位方式
            value: 元素定位方式与值（可选，与 element 二选一）。
            keys: 待输入的文本。
            input_wait: 为 True 时逐字符输入并随机停顿，模拟人工输入。
        """
        if element:
            target = element
        elif by and value:
            target = self.find_element(by, value)
        else:
            self.screenshot("element_not_found")
            raise NoSuchElementException(f"元素未找到: by={by}, value={value}")

        if input_wait:
            for char in keys:
                target.send_keys(char)
                sleep(uniform(0.05, 0.2))
        else:
            target.send_keys(keys)

    def click(
        self,
        by: Optional[str] = None,
        value: Optional[str] = None,
        element: Optional[WebElement] = None
    ) -> None:
        """点击元素（支持直接传入元素或按定位方式查找）。"""
        if element:
            target = element
        elif by and value:
            try:
                target = self.find_element(by, value)
            except NoSuchElementException:
                self.screenshot("element_not_found")
                raise NoSuchElementException(f"元素未找到: by={by}, value={value}")
        else:
            raise ValueError("click() 需要传 element 或 (by, value)")

        target.click()
            

    # --------------------------- 截图 ---------------------------
    def screenshot(self, file_path: str, element: Optional[WebElement] = None) -> None:
        """截图保存。

        Args:
            file_path: 当 element 为 None 时为文件名（自动归入截图目录）；
                       当 element 不为 None 时为元素截图完整路径。
            element: 指定时对单个元素截图，否则对整个页面截图。
        """
        # 元素截图时 file_path 已是完整路径，直接保存并返回；
        # 否则会继续走到整页截图逻辑，把完整路径再拼进目录产生畸形文件名。
        if element:
            element.screenshot(file_path)
            return

        screenshot_dir = f"{PROJECT_ROOT}/ui_test/screenshots/"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        full_path = f"{screenshot_dir}{file_path}{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        self._driver.save_screenshot(full_path)
        print(f"全屏截图已保存到 {full_path}")

    # --------------------------- 生命周期 ---------------------------
    def quit(self) -> None:
        """退出浏览器。"""
        if self._driver:
            self._driver.quit()