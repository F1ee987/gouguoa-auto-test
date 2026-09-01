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
    _FINISH_NEXT_XPATH = '//*[@id="checkBox"]/form/table/tbody/tr[5]/td[2]/div[{action}]'
    APPROVE_COMMENT_INPUT = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[7]/td[2]/textarea') # 审批意见输入框
    CHECK_UNAME = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[5]/td[2]/div[3]/input[1]')#下一个审批人选择框
    NEXT_APPROVER_DEPT = ("xpath", '//*[@id="employeeDepament"]/div/div/div[2]/div[3]/div/div/span[2]') #下一个审批人部门
    NEXT_APPROVER_NAME = ("xpath", '//*[@id="employee"]/span') #下一个审批人姓名
    _BT_XPATH = '//*[@id="checkBox"]/form/div/span[{action}]'
    _CONFIRM_XPATH = '//*[@id="layui-layer{layer}"]/div[4]/a[1]'


    #---------------------------- 定位器 -----------------
    def _confirm_locator(self, action: str) -> tuple:
        """
        生成确认按钮定位器
        :param action: "pass" | "reject"
        """
        layer = 1 if action == "pass" else 3
        return "xpath", self._CONFIRM_XPATH.format(layer=layer)

    def _bt_locator(self, action: str) -> tuple:
        """生成审批按钮定位器"""
        return "xpath", self._BT_XPATH.format(action=action)

    def _finish_or_next_locator(self, action: str) -> tuple:
        """
        :param action: "finish" | "next"
        """
        index = 1 if action == "finish" else 2
        return "xpath", self._FINISH_NEXT_XPATH.format(action=index)

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

    #---------------------------- 操作 --------------------------
    def open_review_center(self, approve_id: Optional[int] = None) -> int:
        """打开审批详情页；不传 id 则自动取一条待审批记录，返回实际使用的 ID"""
        approve_id = approve_id or self._fetch_pending_id()
        if not approve_id:
            raise ValueError("没有待审批的请假记录")
        print("打开审批详情页，实际使用的请假记录 ID:", approve_id)
        self.open(self._review_url(approve_id))
        return approve_id    # 返回给调用方做后续断言

    def _next_approver(self, approval_step: int = 1) -> None:
        """
        是否继续审批，审批结束或审批通过并转交下一审批人
        :param approval_step: 审批步骤（1：审批结束；2：审批通过并转交下一审批人）
        :return: None
        """
        if approval_step == 1:
            self.wait_clickable(*self._finish_or_next_locator('finish')).click()
        elif approval_step == 2:
            self.wait_clickable(*self._finish_or_next_locator('next')).click()
            self.wait_clickable(*self.CHECK_UNAME).click()
            self.wait_clickable(*self.NEXT_APPROVER_DEPT).click()
            self.wait_clickable(*self.NEXT_APPROVER_NAME).click()
        else:
            raise ValueError("无效的审批步骤")

    def approve(self, approval_step: int = 1, comment: str = "同意"):
        """
        审批通过请假申请

        :param approval_step: 审批步骤（1：审批结束；2：审批通过并转交下一审批人）
        :param comment: 审批意见，允许为空字符串
        :return: None
        """
        self._next_approver(approval_step)
        self.send_keys(*self.APPROVE_COMMENT_INPUT, keys=comment)
        self.wait_clickable(*self._bt_locator('1')).click()
        self.wait_present(*self._confirm_locator('pass')).click()    # 确认按钮

    def reject(self, approval_step: int = 1, comment: str = "不同意"):
        """
        拒绝请假申请
        :param approval_step: 审批步骤（1：审批结束；2：审批通过并转交下一审批人）
        :param comment: 审批意见，允许为空字符串
        :return: None
        """
        self._next_approver(approval_step)
        self.send_keys(*self.APPROVE_COMMENT_INPUT, keys=comment)
        self.wait_clickable(*self._bt_locator('2')).click()
        self.wait_present(*self._confirm_locator('reject')).click()    # 拒接确认按钮