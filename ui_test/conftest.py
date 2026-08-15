"""
@Project:gouguoa-auto-test
@File   :conftest.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/15 13:34
"""
from selenium import webdriver
import pytest

@pytest.fixture(scope='session')
def driver():
    d = webdriver.Chrome()
    yield d
    d.close()