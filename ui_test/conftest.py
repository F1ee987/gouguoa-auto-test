"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 13:34
"""
import pytest

@pytest.fixture(scope='function')
def driver():
    from selenium import webdriver
    d = webdriver.Chrome()
    yield d
    d.close()