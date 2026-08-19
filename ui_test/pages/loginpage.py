"""
@Project:gouguoa-auto-test
@File   :loginpage.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/19 13:22
"""
from base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
