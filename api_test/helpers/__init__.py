"""接口测试公共辅助包：响应断言等可复用工具。"""
from .response import assert_api_success, assert_http_ok

__all__ = ['assert_api_success', 'assert_http_ok']
