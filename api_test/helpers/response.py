"""
接口响应断言辅助。

把原先散落在各测试中的「断言状态码 -> 解析 JSON -> 校验 code/msg」逻辑统一为两个函数，
避免重复且容易写错（例如把 logger.error(...) 当作断言消息传入）的断言模式。
"""
import json
from typing import Any

from requests import Response


def assert_http_ok(response: Response, context: str = "") -> None:
    """断言 HTTP 状态码为 200。"""
    prefix = f"{context} " if context else ""
    assert response.status_code == 200, \
        f"{prefix}HTTP 请求失败，状态码: {response.status_code}"


def assert_api_success(
    response: Response,
    expected_code: int = 0,
    expected_msg: str | None = None,
    context: str = "",
) -> dict:
    """断言接口业务返回符合预期，并返回解析后的响应体。

    Args:
        response: requests.Response 对象。
        expected_code: 期望的 code 值，默认 0（成功）。
        expected_msg: 若提供，则要求 msg 包含该子串。
        context: 上下文描述，用于断言失败时定位用例。
    Returns:
        解析后的 JSON 响应体（dict）。
    """
    prefix = f"{context} " if context else ""
    assert_http_ok(response, context)

    try:
        body: dict = response.json()
    except json.JSONDecodeError:
        raise AssertionError(f"{prefix}响应不是有效的 JSON: {response.text}")

    actual_code = body.get('code')
    actual_msg = body.get('msg', '')
    assert actual_code == expected_code, \
        f"{prefix}接口返回非预期 code={actual_code}, msg={actual_msg}"
    if expected_msg is not None:
        assert expected_msg in actual_msg, \
            f"{prefix}接口消息不匹配，期望包含 '{expected_msg}'，实际: {actual_msg}"
    return body
