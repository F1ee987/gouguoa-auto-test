"""
文件读取与缓存清理工具。

提供：
- FileReader：读取 csv / yaml / json 等配置文件；
- delete_cache：删除运行时产生的临时文件或空目录。
"""
import csv
import json
import os
from typing import Any, List
import yaml

class FileReader:
    """配置文件读取器，封装常见格式的一次性读取。"""

    @staticmethod
    def read_csv(file_path: str) -> List[List[str]]:
        """读取 CSV 文件，返回包含所有行的二维列表（含表头）。"""
        with open(file_path, mode='r', encoding='utf-8') as fp:
            return [row for row in csv.reader(fp)]

    @staticmethod
    def read_yaml(file_path: str) -> Any:
        """读取 YAML 文件，返回解析后的对象。"""
        with open(file_path, mode='r', encoding='utf-8') as fp:
            return yaml.safe_load(fp)

    @staticmethod
    def read_json(file_path: str) -> Any:
        """读取 JSON 文件，返回解析后的对象。"""
        with open(file_path, mode='r', encoding='utf-8') as fp:
            return json.loads(fp.read())


def delete_cache(file_path: str, is_directory: bool = False) -> None:
    """删除运行时缓存文件或空目录。

    Args:
        file_path: 待删除的文件或目录路径。
        is_directory: 为 True 时按目录处理（仅删除空目录）。
    """
    try:
        if not os.path.exists(file_path):
            return
        if is_directory:
            os.rmdir(file_path)
        else:
            os.remove(file_path)
    except Exception as e:
        print(f"删除缓存文件时出错: {e}")
