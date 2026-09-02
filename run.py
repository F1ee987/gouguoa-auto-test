"""
统一测试执行入口，支持通过命令行参数筛选测试范围。

示例：
    python run.py                              # 运行全部测试（读取 pytest.ini 配置）
    python run.py --api                        # 仅运行接口测试
    python run.py --ui                         # 仅运行 UI 测试
    python run.py --target api_test/.../test_rbac.py   # 运行指定文件 / 目录
"""
import argparse
import os
import pytest
from typing import List, Optional

def build_pytest_args(targets: Optional[List[str]] = None) -> List[str]:
    """根据筛选目标构造 pytest 命令行参数列表。

    Args:
        targets: 指定的测试用例 / 目录路径；为 None 时运行 pytest.ini 配置的全部范围。
    Returns:
        pytest 接收的参数列表（空列表表示使用默认 testpaths）。
    """
    return list(targets) if targets else []


def run_tests(targets: Optional[List[str]] = None) -> int:
    """调用 pytest 执行测试。

    Args:
        targets: 指定的测试用例 / 目录路径；为 None 时运行 pytest.ini 配置的全部范围。
    Returns:
        pytest 退出码（0 表示全部通过）。
    """
    return pytest.main(build_pytest_args(targets))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="gouguoa 自动化测试统一执行入口",
    )
    # --api / --ui / --target 互斥，避免范围重叠导致重复收集
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--api",
        action="store_true",
        help="仅运行接口测试（api_test/）",
    )
    scope.add_argument(
        "--ui",
        action="store_true",
        help="仅运行 UI 测试（ui_test/）",
    )
    scope.add_argument(
        "--target",
        metavar="PATH",
        help="运行指定文件 / 目录 / 用例（如 api_test/test_cases/test_rbac.py）",
    )
    return parser.parse_args(argv)


def resolve_targets(args: argparse.Namespace) -> Optional[List[str]]:
    """将命令行参数映射为 pytest 目标路径。

    Returns:
        pytest 目标列表；全部参数均未指定时返回 None（运行全部范围）。
    """
    if args.target:
        return [args.target]
    if args.api:
        return ["api_test/"]
    if args.ui:
        return ["ui_test/"]
    return None


def main() -> None:
    args = parse_args()
    targets = resolve_targets(args)
    exit_code = run_tests(targets)
    # 测试结束后生成 Allure HTML 报告（需已安装 allure 命令行）
    os.system("allure generate ./reports/allure-results -o ./reports/html --clean")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
