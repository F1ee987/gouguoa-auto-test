"""
文件读取与缓存清理工具。

提供：
- FileReader：读取 csv / yaml / json 等配置文件；
- delete_cache：删除运行时产生的临时文件或空目录。
"""
import csv
import json
import os
from typing import Any, List, Dict
import yaml
from config.conf import PROJECT_ROOT
from utils.logger import Logger

logger = Logger(__name__)

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
        logger.error(f"删除缓存文件时出错: {e}")

def get_account_by_role(accounts: List[List[str]], role: str) -> Dict[str, Any]:
    """根据角色获取对应的账户名。

    Args:
        role: 角色名称。
        accounts: 账户列表，格式为二维列表，第一列是角色名称，第二列是账户名。

    Returns:
        对应的账户信息。
    """
    account: List[List[str]] = []
    if not accounts:
        logger.error("未找到账户信息")
    for row in accounts:
        if row[0] == role:
           account.append(row[1:])
    if not account:
        logger.error(f"未找到角色 {role} 的账户信息")
        raise ValueError(f"未找到角色 {role} 的账户信息")
    else:
        account_dict: Dict[str, Any] = dict(zip(accounts[0][1:], account[0]))
        return account_dict

if __name__ == "__main__":
    # 示例：读取 CSV 文件
    csv_data = FileReader.read_csv(f'{PROJECT_ROOT}/config/accounts.csv')
    print(csv_data)
    print(get_account_by_role(csv_data,'boss'))