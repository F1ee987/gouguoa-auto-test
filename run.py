"""
统一测试执行入口。

用法：
    python run.py                  # 运行全部测试（读取 pytest.ini 配置）
    python run.py --api            # 仅运行接口测试
    python run.py --ui             # 仅运行 UI 测试
    python run.py --target api_test/test_cases/test_rbac.py   # 运行指定文件/目录
"""
import pytest
from typing import List, Optional

def run_tests(targets: Optional[List[str]] = None) -> int:
    """调用 pytest 执行测试。

    Args:
        targets: 指定的测试用例 / 目录路径；为 None 时运行 pytest.ini 中配置的全部范围。
    Returns:
        pytest 退出码（0 表示全部通过）。
    """
    args = targets if targets else []
    return pytest.main(args)

def main() -> None:
    run_tests()

if __name__ == '__main__':
    main()
