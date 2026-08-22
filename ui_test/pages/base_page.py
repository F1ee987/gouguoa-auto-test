"""
@Project:gouguoa-auto-test
@File   :base_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 14:44
"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from time import sleep
from random import uniform
from typing import Optional
from datetime import datetime
from config.conf import HOME
import os

class BasePage:
    """基础页面操作"""
    def __init__(self, driver: WebDriver) -> None:
        """初始化浏览器驱动

        Args:
            driver (WebDriver): 浏览器驱动实例(必须)
        """
        self._driver = driver
        self.options = Optional[Options]

    def _verify_driver(self) -> None:
        """验证浏览器驱动是否存在"""
        if not self._driver:
            raise ValueError("浏览器驱动未初始化，请确保在创建BasePage实例时传入有效的WebDriver对象。")

    @property
    def title(self) -> str:
        """获取当前页面标题"""
        self._verify_driver()
        return self._driver.title

    def add_options(self, options: Optional[Options]) -> None:
        """添加浏览器选项

        Args:
            options: 浏览器选项实例
        """
        self.options = options

    def open(self, url: str) -> None:
        """打开指定URL

        Args:
            url (str): 要打开的URL
        """
        self._verify_driver()
        try:
            self._driver.get(url)
        except TimeoutError:
            raise TimeoutError(f"打开URL {url} 超时")

    @staticmethod
    def force_wait(seconds: int) -> None:
        """强制等待指定的秒数

        Args:
            seconds (int): 等待的秒数
        """
        sleep(seconds)

    def ec_wait(self, by: str, value: str, timeout: int = 5) -> Optional[WebElement]:
        """使用显式等待查找元素

        Args:
            by (str): 查找方式
            value (str): 查找的值
            timeout (int, optional): 超时时间，默认5秒

        Returns:
            WebElement: 找到的元素
        Raises:
            NoSuchElementException: 如果在指定时间内未找到元素
        """
        self._verify_driver()
        wait = WebDriverWait(self._driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)), message=f"元素未找到: {by}={value}，等待了{timeout}秒")

    def find_element(self, by: str, value: str) -> Optional[WebElement]:
        """查找元素

        Args:
            by (str): 查找方式
            value (str): 查找的值

        Returns:
            WebElement: 找到的元素
        """
        self._verify_driver()
        return self._driver.find_element(by, value)

    def send_keys(
            self, element: Optional[WebElement],
            by: Optional[str] = None, value: Optional[str] = None, 
            keys: str = '', 
            input_wait: bool = False
        ) -> None:
        """向指定元素发送键盘输入
        可以通过直接传入元素，或者通过查找方式和查找值来定位元素。
        Args:
            element (WebElement, optional): 要发送键盘输入的元素
            by (str): 查找方式
            value (str): 查找的值
            keys (str): 要发送的键盘输入
            input_wait (bool, optional): 是否模拟手动输入的等待时间，默认False
        """
        self._verify_driver()
        target = element if element else self.find_element(by, value) if by and value else None
        if not target:
            self.screenshot(f'{HOME}/docs/')
            raise NoSuchElementException(f"元素未找到: by={by}, value={value}")
        
        if input_wait:
            for char in keys:
                target.send_keys(char)
                sleep(uniform(0.05, 0.2))
        else:
            target.send_keys(keys)

    def click(self, element: Optional[WebElement], by: Optional[str] = None, value: Optional[str] = None) -> None:
        """点击指定元素
        可以通过直接传入元素，或者通过查找方式和查找值来定位元素。
        Args:
            element (WebElement, optional): 要点击的元素
            by (str): 查找方式
            value (str): 查找的值
        """
        self._verify_driver()
        target = element if element else self.find_element(by, value) if by and value else None
        if not target:
            self.screenshot(f'{HOME}/docs/')
            raise NoSuchElementException(f"元素未找到: by={by}, value={value}")
        
        target.click()

    def screenshot(self, file_path: str, element: Optional[WebElement] = None) -> None:
        """截图并保存到指定路径
        Args:
            file_path (str): 截图保存的路径（若element为None，则为目录路径，会自动生成文件名）
            element (WebElement, optional): 要截图的元素
        """
        self._verify_driver()
        if element:
            element.screenshot(file_path)
        else:
            base_path = f"{HOME}/ui_test/screenshots/"
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            full_path = f"{base_path}{file_path}{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            self._driver.save_screenshot(full_path)
            print(f"全屏截图已保存到 {full_path}")

    @property
    def current_url(self) -> str:
        """获取当前页面URL"""
        self._verify_driver()
        return self._driver.current_url

    def quit(self) -> None:
        """退出浏览器"""
        if self._driver:
            self._driver.quit()
