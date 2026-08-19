"""
@Project:gouguoa-auto-test
@File   :run.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/9 14:08
"""
import pytest

def only_run_api_test():
    """
    只运行api测试用例
    :return:
    """
    pytest.main(["./api_test/test_cases"])

def only_run_ui_test():
    """
    只运行ui测试用例
    :return:
    """
    pytest.main(["./ui_test/test_cases"])

def run_all_test():
    """
    运行所有测试用例
    :return:
    """
    pytest.main()

if __name__ == '__main__':
    only_run_api_test()