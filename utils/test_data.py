"""
测试数据加载：从 CSV 读取账号与参数化用例。

将原先散落在各测试文件中的「读 CSV -> 组装参数 -> 生成 ids」逻辑统一收敛到这里，
并提供通用加载器 load_parametrized_csv，避免重复造轮子。
"""
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple
import pytest
from config.conf import PROJECT_ROOT
from utils.file_reader import FileReader


def load_accounts() -> List[List[str]]:
    """读取账号配置文件 config/accounts.csv，返回全部行（含表头）。"""
    csv_path = Path(PROJECT_ROOT) / 'config' / 'accounts.csv'
    return FileReader.read_csv(str(csv_path))


@lru_cache(maxsize=None)
def prepare_account() -> tuple[list[tuple], list[str]]:
    """准备登录接口所需的参数化账号数据（带缓存，进程内只解析一次）。

    Returns:
        (test_data, test_ids)：
        - test_data 为 (username, password, expected_code) 元组列表；
        - test_ids 为对应的用例描述，用作 pytest 参数化的 id。
    """
    accounts_path = Path(PROJECT_ROOT) / 'config' / 'accounts.csv'
    return load_parametrized_csv(
        accounts_path,
        data_columns=[1, 2, 3],  # username, password, expected_code
        id_column=4,             # description
        min_fields=5,
    )


def load_parametrized_csv(
    file_path: str | Path,
    *,
    data_columns: List[int],
    id_column: int,
    min_fields: int = 0,
) -> Tuple[List[Tuple], List[str]]:
    """通用 CSV 参数化数据加载器，跳过表头。

    用于把任意「数据 + 描述」型 CSV 转换为 pytest.parametrize 所需的
    (cases, ids) 二元组。

    Args:
        file_path: CSV 文件路径。
        data_columns: 作为用例参数的列索引列表。
        id_column: 作为 pytest 用例 id 的列索引。
        min_fields: 每行最少字段数，不足则跳过（用于过滤残缺行）。
    Returns:
        (cases, ids)：cases 为参数元组列表，ids 为用例描述列表。
    """
    rows = FileReader.read_csv(str(file_path))
    if not rows:
        pytest.skip(f"测试数据文件为空或不存在: {file_path}")

    cases: List[Tuple] = []
    ids: List[str] = []
    for row in rows[1:]:  # 跳过表头
        if len(row) < min_fields:
            print(f"⚠ 跳过字段不完整的数据行：{row}")
            continue
        cases.append(tuple(row[i] for i in data_columns))
        ids.append(row[id_column].strip())

    if not cases:
        pytest.skip("没有有效的测试数据")
    return cases, ids
