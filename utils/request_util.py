"""
@Project:gouguoa-auto-test
@File   :request_util.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/18 14:26
"""
import requests
from typing import Optional

class RequestHandle:
    """请求操作类"""
    def __init__(self, use_session: bool = False):
        """
        :param use_session: 是否自动创建并启用 requests.Session（True 则创建，False 则不使用 Session）
        """
        self.session: Optional[requests.Session] = (
            requests.Session() if use_session else None
        )

    def __request(self, method: str, url: str, **kwargs) -> requests.Response:
        if self.session:
            return self.session.request(method=method, url=url, **kwargs)
        return requests.request(method=method, url=url, **kwargs)

    def get(self, url: str, **kwargs) -> requests.Response:
        return self.__request(method='GET', url=url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self.__request('POST', url, **kwargs)

    def close(self) -> None:
        if self.session:
            self.session.close()