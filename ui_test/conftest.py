"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 13:34
"""
import pytest

@pytest.fixture(scope='session')
def driver():
    from selenium import webdriver
    d = webdriver.Chrome()
    yield d
    print("关闭浏览器1")
    d.quit()
