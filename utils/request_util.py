"""
HTTP 请求封装：在 requests 之上提供统一的会话（Session）管理能力。

设计目标：
- 支持「无状态」（单次 requests 调用）与「有状态」（requests.Session，自动保持 Cookie）两种模式；
- 对外暴露语义清晰的 get / post 等方法；
- 便于测试用例复用同一个会话，从而保持登录态。
"""
import requests
from typing import Any, Optional


class RequestHandle:
    """HTTP 请求处理器，可选启用 Session 以维持 Cookie。"""

    def __init__(self, use_session: bool = False):
        """
        Args:
            use_session: 为 True 时创建 requests.Session（自动保持 Cookie），
                         为 False 时使用无状态 requests 发送请求。
        """
        self.session: Optional[requests.Session] = (
            requests.Session() if use_session else None
        )

    def add_cookie(self, cookie: Any) -> None:
        """向会话中追加 Cookie（仅在启用 Session 时生效）。"""
        if self.session:
            self.session.cookies.update(cookie)

    def _send_request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """统一的请求入口：启用 Session 时走 Session，否则走 requests。"""
        if self.session:
            return self.session.request(method=method, url=url, **kwargs)
        return requests.request(method=method, url=url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 GET 请求。"""
        return self._send_request(method="GET", url=url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 POST 请求。"""
        return self._send_request(method="POST", url=url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 DELETE 请求。"""
        return self._send_request(method="DELETE", url=url, **kwargs)

    def close(self) -> None:
        """关闭会话（仅在启用 Session 时生效）。"""
        if self.session:
            self.session.close()
