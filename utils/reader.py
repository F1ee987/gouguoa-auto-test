"""
@Project:gouguoa-auto-test
@File   :reader.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/7/23 13:55
"""
import csv
import yaml
import json

class Reader:
    @staticmethod
    def read_csv(file_path):
        """
        读取csv文件
        :param file_path: 文件路径
        :return: 返回csv文件内容
        """
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            load_data = []
            for row in reader:
                load_data.append(row)
            return load_data

    @staticmethod
    def read_yaml(file_path):
        """
        读取yaml文件
        :param file_path: 文件路径
        :return: 返回yaml文件内容
        """
        with open(file_path, mode='r', encoding='utf-8') as file:
            load_data = yaml.safe_load(file)
            return load_data

    @staticmethod
    def read_json(file_path):
        """
        读取json文件
        :param file_path: 文件路径
        :return:
        """
        with open(file_path, mode='r', encoding='utf-8') as file:
            load_data = json.loads(file.read())
            return load_data

if __name__ == '__main__':
    reader = Reader()
    data = reader.read_csv('../config/accounts.csv')
    print(data[1])
