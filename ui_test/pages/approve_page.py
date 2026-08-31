"""
@Project:conf.py
@File   :approve_page.py
@IDE    :PyCharm
@Author :zhousha
@Date   :2026/8/31 13:05
"""
from ui_test.pages import BasePage
from selenium.webdriver.remote.webdriver import WebDriver
from random import randint

class ApproveApplyPage(BasePage):
    """发起审批页
    选择审批类型 -> 填写表单 -> 选择审批人 -> 提交
    """
    CLICK_APPROVE_LOC = ("xpath", "/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/a")
    APPROVE_TYPE_MAP = {
        "REQUEST_LEAVE" : ("xpath", "/html/body/div[1]/div/div[3]/div/div[1]"), #请假
        "REIMBURSEMENT": ("xpath", "/html/body/div[1]/div/div[9]/div/div[1]"), #报销
        "ONBOARDING": ("xpath", "/html/body/div[1]/div/div[11]/div/div[1]") #入职
    }

    # -------------------------- 请假定位器 ---------------------------------------
    # START_DATE_INPUT_LOC = ("xpath", "/html/body/form/table/tbody/tr[1]/td[2]/input") #开始时间框展开
    # START_DATE_SELECT_NOW_LOC = ("xpath", '//*[@id="layui-laydate1"]/div[2]/div/span[2]') #开始时间选择现在
    # START_DATE_CONFIRM_LOC = ("xpath", '//*[@id="layui-laydate1"]/div[2]/div/span[3]') #确认开始时间

    # END_DATE_INPUT_LOC = ("xpath", '/html/body/form/table/tbody/tr[1]/td[4]/input')
    # END_DATE_SELECT_NOW_LOC = ("xpath", '//*[@id="layui-laydate7"]/div[2]/div/span[2]')
    # END_DATE_CONFIRM_LOC = ("xpath", '//*[@id="layui-laydate7"]/div[2]/div/span[3]')
    # 日期输入框
    START_DATE_INPUT_LOC = ("xpath", "/html/body/form/table/tbody/tr[1]/td[2]/input")
    END_DATE_INPUT_LOC   = ("xpath", "/html/body/form/table/tbody/tr[1]/td[4]/input")

    # laydate 弹窗按钮（不再区分 start/end，统一用）
    LAYDATE_NOW_BTN    = ("xpath", "//div[contains(@class,'layui-laydate')]/div[2]/div/span[2]")
    LAYDATE_CONFIRM_BTN = ("xpath", "//div[contains(@class,'layui-laydate')]/div[2]/div/span[3]")

    LEAVE_DATE_LOC = ("xpath", '/html/body/form/table/tbody/tr[2]/td[2]/input') #请假时长
    LEAVE_TYPE_SELECT_LOC = ("xpath", '/html/body/form/table/tbody/tr[2]/td[4]/div/div/input') #请假类型下拉框

    LEAVE_TYPE_LOC = ("xpath", f'/html/body/form/table/tbody/tr[2]/td[4]/div/dl/dd[{randint(2,10)}]') #请假类型随机
    REASON_INPUT_LOC = ("xpath", '/html/body/form/table/tbody/tr[3]/td[2]/textarea') #请假理由
    APPROVE_PROCESS_SELECT_LOC = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[1]/td[2]/div/div/input') #请假流程下拉框
    APPROVE_TYPE_LOC = ("xpath", '//*[@id="checkBox"]/form/table/tbody/tr[1]/td[2]/div/dl/dd[2]')

    APPROVE_PERSON_CHECKBOX_LOC = ("xpath", '//*[@id="checkTR"]/td[2]/input[1]') #审批人chechKTR
    EMPLOYEEDEPAMENT_LOC = ("xpath", '//*[@id="employeeDepament"]/div/div/div[2]/div[1]/div/div/span[2]')
    APPROVE_PERSON = ("xpath", '//*[@id="employee"]/span[2]') #选择人事经理审批

    SUBMIT_BT = ("xpath", '/html/body/form/div[2]/button[1]') #提交按钮

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
        self.wait_clickable(*locator)

    def fill_leave_form(self) -> None:
        """填写请假表单"""
        self.select_approve_type("REQUEST_LEAVE")
        self.wait_clickable(*self.START_DATE_INPUT_LOC)
        self.click(*self.LAYDATE_NOW_BTN)
        self.click(*self.LAYDATE_CONFIRM_BTN)
        