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
        self._driver = driver
        self.options: Optional[Options] = None

    # --------------------------- 内部工具 ---------------------------
    def _verify_driver(self) -> None:
        """校验浏览器驱动已初始化。"""
        if not self._driver:
            raise ValueError("浏览器驱动未初始化，请确保在创建 BasePage 实例时传入有效的 WebDriver 对象。")

    def _resolve_element(
        self,
        element: Optional[WebElement],
        by: Optional[str],
        value: Optional[str],
    ) -> Optional[WebElement]:
        """解析目标元素：优先使用直接传入的元素，否则按定位方式查找。"""
        if element:
            return element
        if by and value:
            return self.find_element(by, value)
        return None

    # --------------------------- 属性 / 配置 ---------------------------
    @property
    def title(self) -> str:
        """当前页面标题。"""
        self._verify_driver()
        return self._driver.title

    @property
    def current_url(self) -> str:
        """当前页面 URL。"""
        self._verify_driver()
        return self._driver.current_url

    def add_options(self, options: Optional[Options]) -> None:
        """附加浏览器启动选项。"""
        self.options = options

    # --------------------------- 导航 / 等待 ---------------------------
    def open(self, url: str) -> None:
        """打开指定 URL。"""
        self._verify_driver()
        self._driver.get(url)

    @staticmethod
    def force_wait(seconds: int) -> None:
        """强制休眠指定秒数（仅用于无法显式等待的过渡场景）。"""
        sleep(seconds)

    def ec_wait(self, by: str, value: str, timeout: int = 5) -> Optional[WebElement]:
        """使用显式等待查找元素，超时未找到则抛出 NoSuchElementException。"""
        self._verify_driver()
        wait = WebDriverWait(self._driver, timeout)
        return wait.until(
            EC.presence_of_element_located((by, value)),
            message=f"元素未找到: {by}={value}，等待了 {timeout} 秒",
        )

    # --------------------------- 元素操作 ---------------------------
    def find_element(self, by: str, value: str) -> WebElement:
        """按定位方式查找元素（找不到由 Selenium 抛异常）。"""
        self._verify_driver()
        return self._driver.find_element(by, value)

    def send_keys(
        self,
        element: Optional[WebElement] = None,
        by: Optional[str] = None,
        value: Optional[str] = None,
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
        self._verify_driver()
        target = self._resolve_element(element, by, value)
        if not target:
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
        element: Optional[WebElement] = None,
        by: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        """点击元素（支持直接传入元素或按定位方式查找）。"""
        self._verify_driver()
        target = self._resolve_element(element, by, value)
        if not target:
            self.screenshot("element_not_found")
            raise NoSuchElementException(f"元素未找到: by={by}, value={value}")
        target.click()

    # --------------------------- 截图 ---------------------------
    def screenshot(self, file_path: str, element: Optional[WebElement] = None) -> None:
        """截图保存。

        Args:
            file_path: 当 element 为 None 时为文件名（自动归入截图目录）；
                       当 element 不为 None 时为元素截图完整路径。
            element: 指定时对单个元素截图，否则对整个页面截图。
        """
        self._verify_driver()
        if element:
            element.screenshot(file_path)
            return

        screenshot_dir = f"{PROJECT_ROOT}/ui_test/screenshots/"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        full_path = f"{screenshot_dir}{file_path}{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        self._driver.save_screenshot(full_path)
        print(f"全屏截图已保存到 {full_path}")

    # --------------------------- 生命周期 ---------------------------
    def quit(self) -> None:
        """退出浏览器。"""
        if self._driver:
            self._driver.quit()