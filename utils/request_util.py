"""
@Project:gouguoa-auto-test
@File   :request_util.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/18 14:26
"""
import requests
from typing import Optional, Any

class RequestHandle:
    """请求操作类"""
    def __init__(self, use_session: bool = False):
        """
        :param use_session: 是否自动创建并启用 requests.Session（True 则创建，False 则不使用 Session）
        """
        self.session: Optional[requests.Session] = (
            requests.Session() if use_session else None
        )

    def add_cookie(self, cookie: Any) -> None:
        """添加 Cookie"""
        if self.session:
            self.session.cookies.update(cookie)

    def __request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """
        发送请求,
        如果使用了 Session，则使用 Session 发送请求，否则直接使用 requests 发送请求
        """
        if self.session:
            return self.session.request(method=method, url=url, **kwargs)
        return requests.request(method=method, url=url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 GET 请求"""
        return self.__request(method='GET', url=url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """发送 POST 请求"""
        return self.__request('POST', url, **kwargs)

    def close(self) -> None:
        """关闭 Session,如果使用了 Session """
        if self.session:
            self.session.close()