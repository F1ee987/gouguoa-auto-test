"""
@Project: gouguoa-auto-test
@File   : file_reader.py
@IDE    : PyCharm
@Author : zhousha
@Date   : 2026/7/23 13:55
"""
import csv
import yaml
import json
from typing import List, Any, Tuple
import pytest
import os
from config.conf import HOME

class Reader:
    @staticmethod
    def read_csv(file_path: str) -> List[List[str]]:
        """
        读取csv文件
        :param file_path: 文件路径
        :return: 返回csv文件内容
        """
        with open(file_path, mode='r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            loaded_rows: List[List[str]] = []
            for row in csv_reader:
                loaded_rows.append(row)
            return loaded_rows

    @staticmethod
    def read_yaml(file_path: str) -> Any:
        """
        读取yaml文件
        :param file_path: 文件路径
        :return: 返回yaml文件内容
        """
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data

    @staticmethod
    def read_json(file_path: str) -> Any:
        """
        读取json文件
        :param file_path: 文件路径
        :return:
        """
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = json.loads(f.read())
            return data

#_________________配置函数____________________
def del_cache(filepath: str, is_directory: bool = False) -> None:
    """删除缓存文件
    :param filepath: 文件路径
    :param is_directory: 是否是目录"""
    try:
        if is_directory:
            if os.path.exists(filepath):
                os.rmdir(filepath)
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
    except Exception as e:
        print(f"删除缓存文件时出错: {e}")

def get_test_accounts() -> List[List[str]]:
    """读取accounts.csv文件返回测试账号数据"""
    file_reader = Reader()
    return file_reader.read_csv(f'{HOME}/config/accounts.csv')

def prepare_account() -> Tuple[List[Tuple[str, str, str]], List[str]]:
    """准备测试所需的账号信息"""
    accounts = get_test_accounts()
    if not accounts:
        pytest.skip("未读取到测试账号")

    test_data: List[Tuple[str, str, str]] = []
    test_ids: List[str] = []
    for account in accounts[1:]:
        username = account[1]
        password = account[2]
        expected_code = account[3]
        description = account[4]          # 原名 describe → description
        print(f"🚀 加载测试账号: {username}")
        test_data.append((username, password, expected_code))
        test_ids.append(description)

    if not test_data and not test_ids:
        pytest.skip("没有有效的测试账号")

    return test_data, test_ids

if __name__ == '__main__':
    reader = Reader()
    rows = reader.read_csv('../config/accounts.csv')   # 原名 data → rows
    print(rows[1])