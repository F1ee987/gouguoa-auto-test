"""
@Project:conf.py
@File   :approve_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/31 13:05
"""
from ui_test.pages import BasePage
from selenium.webdriver.remote.webdriver import WebDriver

class ApproveApplyPage(BasePage):
    """发起审批页
    选择审批类型 -> 填写表单 -> 选择审批人 -> 提交
    """
    CLICK_APPROVE_LOC = ("xpath", "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/a")
    APPROVE_TYPE_MAP = {
        "REQUEST_LEAVE" : ("xpath", "/html/body/div[1]/div/div[3]/div/div[1]/div/i"), #请假
        "REIMBURSEMENT": ("xpath", "/html/body/div[1]/div/div[9]/div/div[1]/div/i"), #报销
        "ONBOARDING": ("xpath", "/html/body/div[1]/div/div[11]/div/div[1]/div") #入职
    }

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def select_approve_type(self, approve_type: str):
        """
        选择审批类型

        Args:
            approve_type: APPROVE_TYPE_MAP 的 key，如 "REQUEST_LEAVE"
        """
        self.click(*self.CLICK_APPROVE_LOC)
        locator = self.APPROVE_TYPE_MAP.get(approve_type)
        if not locator:
            raise ValueError(f"未定义的审批类型: {approve_type}，可选: {list(self.APPROVE_TYPE_MAP.keys())}")
        self.click(*locator)

    def fill_leave_form(self) -> None:
        """填写请假表单"""
        self.select_approve_type("REQUEST_LEAVE")
        