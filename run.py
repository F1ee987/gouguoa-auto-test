"""
统一测试执行入口。
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
