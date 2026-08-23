"""
统一测试执行入口。

用法：
    python run.py                  # 运行全部测试（读取 pytest.ini 配置）
    python run.py --api            # 仅运行接口测试
    python run.py --ui             # 仅运行 UI 测试
    python run.py --target api_test/test_cases/test_rbac.py   # 运行指定文件/目录
"""
import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="gouguoa 自动化测试执行入口")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--api", action="store_true", help="仅运行接口测试")
    group.add_argument("--ui", action="store_true", help="仅运行 UI 测试")
    parser.add_argument(
        "--target", nargs="*", default=None,
        help="指定要运行的 pytest 路径（可多个），如 --target api_test/test_cases/test_rbac.py",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.api:
        run_tests(["./api_test/test_cases"])
    elif args.ui:
        run_tests(["./ui_test/test_cases"])
    elif args.target:
        run_tests(args.target)
    else:
        run_tests()


if __name__ == '__main__':
    main()
