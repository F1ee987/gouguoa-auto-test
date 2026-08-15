"""
@Project:gouguoa-auto-test
@File   :base_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 14:44
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver, WebElement

class BasePage:
    """基础页面操作"""
    def __init__(self, driver: WebDriver):
        self.__driver = driver

    def open(self, url: str):
        if self.__driver:
            self.__driver.get(url)
