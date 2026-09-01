"""
@Project:conf.py
@File   :approval_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/9/1 11:58
"""
from ui_test.pages import BasePage
from selenium.webdriver.remote.webdriver import WebDriver
from config.conf import BASE_URL
from utils import DataBaseConnection
from typing import Optional
from enum import IntEnum

class LeaveStatus(IntEnum):
    """请假状态枚举"""
    PENDING = 1   # 待审批
    APPROVED = 2  # 已通过
    REJECTED = 3  # 已驳回

class ApprovalPage(BasePage):
    """经理审批页面"""
    APPROVE_FINISHED_BT = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[5]/td[2]/div[1]')
    APPROVE_COMMENT_INPUT = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[7]/td[2]/textarea')
    BT_TEMPLATE = ("xpath", '//*[@id="checkBox"]/form/div/span[{action}]')

    def __init__(self, driver: WebDriver, db: Optional[DataBaseConnection] = None):
        super().__init__(driver)
        if not db:
            raise ValueError("数据库连接对象不能为空")
        self.db = db

    def _fetch_pending_id(self) -> Optional[int]:
        """查询一条待审批的请假记录 ID"""
        rows = self.db.query(
            "SELECT id FROM oa_leaves "
            "WHERE check_status = %s ORDER BY id DESC LIMIT 1",
            (LeaveStatus.PENDING,)
        )
        # 按你的 db 封装调整取值方式：dict 用 rows[0]["id"]，tuple 用 rows[0][0]
        return rows[0]["id"] if rows else None

    @staticmethod
    def _review_url(approve_id: int) -> str:
        """返回指定请假记录的审批页面 URL"""
        return f"{BASE_URL}/home/leaves/view?id={approve_id}"

    def open_review_center(self, approve_id: Optional[int] = None) -> int:
        """打开审批详情页；不传 id 则自动取一条待审批记录，返回实际使用的 ID"""
        approve_id = approve_id or self._fetch_pending_id()
        if not approve_id:
            raise ValueError("没有待审批的请假记录")
        self.open(self._review_url(approve_id))
        return approve_id    # 返回给调用方做后续断言

    def approve(self, comment: str = "同意"):
        """通过请假申请"""
        self.wait_clickable(*self.APPROVE_FINISHED_BT)
        self.send_keys(*self.APPROVE_COMMENT_INPUT, keys=comment)
        self.wait_clickable(*self.BT_TEMPLATE.format(action=1))

    def reject(self, comment: str = "不同意"):
        """拒绝请假申请"""
        self.wait_clickable(*self.APPROVE_FINISHED_BT)
        self.send_keys(*self.APPROVE_COMMENT_INPUT, keys=comment)
        self.wait_clickable(*self.BT_TEMPLATE.format(action=2))